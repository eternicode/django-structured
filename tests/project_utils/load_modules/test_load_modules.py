import os
import shutil
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import List, Tuple

import pytest
import yaml

yaml_dir = Path(__file__).resolve().parent


def make_package(data) -> Tuple[ModuleType, List[str]]:
    """
    Create a package from a dict of contents.

    Returns the constructed package and a lst of modules imported while
    importing the package (not including the package name itself).
    """
    tmpdir = tempfile.mkdtemp()

    def _construct(data, dir):
        for key, value in data.items():
            # Recurse into sub-packages
            if isinstance(value, dict):
                subdir = os.path.join(dir, key)
                os.makedirs(subdir, exist_ok=True)
                _construct(value, subdir)
            # Write module (None = no content)
            else:
                with open(os.path.join(dir, key), "w") as file:
                    file.write(value or "")

    _construct(data, tmpdir)

    sys.path = [".", tmpdir] + sys.path
    modules_before = set(sys.modules.keys())
    try:
        result = __import__(list(data.keys())[0])
    finally:
        modules_imported = set(sys.modules.keys()) - modules_before
        for module in modules_imported:
            del sys.modules[module]
        sys.path = sys.path[2:]
        shutil.rmtree(tmpdir)

    return result, modules_imported


def get_exception(name: str) -> Exception:
    """
    Given a string path to an exception class, import and return that class.
    """
    if "." in name:
        exc_mod, _, exc_name = name.rpartition(".")
        exc_mod = __import__(exc_mod, fromlist=[exc_name])
        return getattr(exc_mod, exc_name)
    else:
        return __builtins__[name]


@pytest.mark.parametrize(
    "yaml_file",
    [pytest.param(file, id=file.name) for file in yaml_dir.glob("**/*.yaml")],
)
def test_load_modules(yaml_file):
    """
    Test for the load_modules function.

    For each yaml file in this directory:

    * Load the yaml file
    * Using the "package" key, construct and import a python package with the
        given contents
    * Using the "tests" key, examine the resulting package

    Supported tests:

    * raises (str or list): Either the name of the exception expected, or a
        two-element list of [exception name, exception match], where "exception
        match" is a string that will be passed to pytest.raises().
    * all (list): Asserts that the package's __all__ matches the given list
    * globals_absent (list): Asserts that the package does not have the given
        names as globals
    * globals_present (list): Asserts that the package has the given names as
        globals
    * globals_values (dict): Asserts that the package's globals have the given
        values
    * modules_imported (list): Asserts that, when imported, the package
        imported the given modules
    """
    with yaml_file.open("r") as file:
        yaml_contents = yaml.safe_load(file)

    pkg_tree = {"package": yaml_contents["package"]}
    tests = yaml_contents.get("tests") or {}

    exc_class = None
    exc_msg = None
    if "raises" in tests:
        exc_info = tests["raises"]
        if isinstance(exc_info, str):
            exc_class = get_exception(exc_info)
        else:
            exc_class = get_exception(exc_info[0])
            exc_msg = exc_info[1]

    if exc_class is not None:
        with pytest.raises(exc_class, match=exc_msg):
            pkg, modules_imported = make_package(pkg_tree)
    else:
        pkg, modules_imported = make_package(pkg_tree)

    if "modules_imported" in tests:
        assert set(tests["modules_imported"]) == set(modules_imported)

    # Testing __all__ is comprehensive
    if "all" in tests:
        assert hasattr(pkg, "__all__")
        assert set(tests["all"]) == set(pkg.__all__)

    # Testing absent globals is not comprehensive
    if "globals_absent" in tests:
        for name in tests["globals_absent"]:
            assert not hasattr(pkg, name), f"Global {name} found unexpectedly"

    # Testing present globals is not comprehensive
    if "globals_present" in tests:
        for name in tests["globals_present"]:
            assert hasattr(pkg, name), f"Missing global {name}"

    # Testing module contents
    if "globals_values" in tests:
        for name, value in tests["globals_values"].items():
            assert getattr(pkg, name) == value, (
                f"Global {name} has wrong value (Expected: {value}, "
                f"Actual: {getattr(pkg, name)})"
            )

    assert yaml_contents is not None
