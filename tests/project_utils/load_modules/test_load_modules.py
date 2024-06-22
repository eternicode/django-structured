import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path
from types import ModuleType
from typing import List

import pytest
import yaml

yaml_dir = Path(__file__).resolve().parent


def make_package(data) -> BaseException | ModuleType:
    """
    Create a package from a dict of contents.

    Returns either the constructed package, or the exception raised when
    importing it.
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
    try:
        result = __import__("package")
    except Exception as e:
        result = e
        result.__formatted_traceback__ = "\n".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        )
    sys.path = sys.path[2:]

    shutil.rmtree(tmpdir)

    return result


def get_exception_list(name_list: List[str]) -> List[Exception]:
    results = []

    if isinstance(name_list, str):
        name_list = [name_list]
    for exception in name_list:
        if "." in exception:
            exc_mod, _, exc_name = exception.rpartition(".")
            exc_mod = __import__(exc_mod, fromlist=[exc_name])
            results.append(getattr(exc_mod, exc_name))
        else:
            results.append(__builtins__[exception])

    return results


@pytest.mark.parametrize("yaml_file", yaml_dir.glob("*.yaml"))
def test_load_yaml_files(subtests, yaml_file):
    """ """
    with yaml_file.open("r") as file:
        yaml_contents = yaml.safe_load(file)

    pkg_tree = {"package": yaml_contents["package"]}
    tests = yaml_contents.get("tests") or {}

    pkg = make_package(pkg_tree)

    # An exception was expected
    if "raises" in tests:
        assert isinstance(pkg, get_exception_list(tests["raises"]))
    else:
        assert not isinstance(pkg, BaseException), getattr(
            pkg,
            "__formatted_traceback__",
            "",
        )

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
