import logging
import pkgutil
from collections import defaultdict
from importlib import import_module
from importlib.util import module_from_spec
from pathlib import Path
from typing import Dict, Iterable, List

from traitlets import default

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def load_modules(
    path,
    globals_dict: Dict | None = None,
    all_names: List | None = None,
    *,
    recursive: bool = False,
    error_on_globals_conflict: bool = True,
    subclasses_of: type | Iterable[type] | None = None,
    instances_of: type | Iterable[type] | None = None,
    of_types: type | Iterable[type] | None = None,
) -> None:
    """
    For use in a package's __init__ module, executes import on all modules in
    the package, optionally adding members to the given globals and __all__.

    Usage examples:
        load_modules(__path__)

        load_modules(__path__, globals())

        __all__ = []
        load_modules(__path__, globals(), __all__)

        from django.db import models
        __all__ = []
        load_modules(__path__, globals(), __all__, subclasses_of=models.Model)

    Args:
        path (str): The package path list to load modules from. Just pass
            __path__ for most cases.

        globals_dict (dict): The globals dictionary of the importing module, to
            which members of the imported modules will be added. This is not
            generally recommended, as naming conflicts can cause unpredictable
            behavior. Naing conflicts will be raised as exceptions unless
            error_on_globals_conflict is set to False.
        all_names (list): The __all__ of the importing module, to which imported
            members' names will be added.

        recursive (bool): Whether to recurse into sub-packages. By default,
            only direct child modules are loaded.
        error_on_globals_conflict (bool): Whether to raise an exception if a
            naming conflict is detected when adding members to the globals
            dictionary. If False, clobbering will be enabled and results may be
            unpredictable.
        subclasses_of (iterable of types): If provided, only members that are
            subclasses of any of the types listed will be added to the globals
            dictionary and/or __all__ list.
        instances_of (iterable of types): If provided, only members that are
            instances of any of the types listed will be added to the globals
            dictionary and/or __all__ list.
        of_types (iterable of types): If provided, this list is added to both
            subclasses_of and instances_of lists (even if they are not
            provided).
    """
    log.debug(f"{path=}")
    if of_types is not None:
        subclasses_of = (subclasses_of or []) + (of_types or [])
        instances_of = (instances_of or []) + (of_types or [])

    if globals_dict is None and all_names is not None:
        log.warning("Populating __all__ but not globals. This is not recommended.")

    names_in_modules = {}

    def _load_modules(
        current_package_path: List[str],
    ) -> None:
        """
        Handle actual import logic and recursion.
        """
        pkg_name = ".".join(current_package_path)

        # __start_path = current_package_path
        log.debug(f"{current_package_path=} {pkg_name=}")

        for finder, module_name, is_pkg in pkgutil.iter_modules(path):
            log.debug(f"{finder=} {module_name=} {is_pkg=}")
            # spec = finder.find_spec(module_name)
            # module = module_from_spec(spec)
            # spec.loader.exec_module(module)
            # module = __import__(f"{pkg_name}.{module_name}", fromlist=[])
            log.debug(f"import_module({pkg_name}.{module_name})")
            module = import_module(f"{pkg_name}.{module_name}")

            if globals_dict is not None or all_names is not None:
                log.debug(f"Examining contents of {module!r}")
                for name in dir(module):
                    # All modules have native dunders, plus dunders are generally
                    # considered Very Private
                    if name.startswith("__") and name.endswith("__"):
                        continue

                    log.debug(f"{name=}")

                    obj = getattr(module, name)
                    log.debug(f"{obj=}")

                    # # Only globalize certain things
                    # if hasattr(obj, "__module__"):
                    #     # Is class
                    #     inst_module = None
                    #     cls_module = obj.__module__
                    # elif hasattr(type(obj), "__module__"):
                    #     # Is instance
                    #     inst_module = __current_path
                    #     cls_module = type(obj).__module__
                    # else:
                    #     # Is something else
                    #     inst_module = __current_path
                    #     cls_module = __current_path
                    # print(module, name, inst_module, cls_module)
                    # # if obj_module not in [__current_path, 'builtins']:

                    # Only globalize the specified types
                    if subclasses_of is not None or instances_of is not None:
                        is_desired_subclass = True
                        if subclasses_of is not None:
                            try:
                                is_desired_subclass = issubclass(obj, subclasses_of)
                            except:
                                is_desired_subclass = False

                        is_desired_instance = True
                        if instances_of is not None:
                            try:
                                is_desired_instance = isinstance(obj, instances_of)
                            except:
                                is_desired_instance = False

                        if not is_desired_subclass and not is_desired_instance:
                            log.debug(
                                f"Skipping {name} because it's not a subclass of "
                                f"{subclasses_of} or an instance of {instances_of}"
                            )
                            continue

                    # Populate globals
                    if globals_dict is not None:
                        log.debug(f"Adding {name} to globals")
                        if name in names_in_modules and error_on_globals_conflict:
                            raise NameError(
                                f"Duplicate name '{name}' in modules '{pkg_name}.{module_name}' and "
                                f"'{names_in_modules[name]}'"
                            )
                        names_in_modules[name] = f"{pkg_name}.{module_name}"
                        globals_dict[name] = obj

                    # Populate __all__
                    if all_names is not None:
                        log.debug(f"Adding {name} to __all__")
                        all_names.append(name)

            if is_pkg and recursive:
                log.debug(f"Recursing into {module_name}")
                _load_modules(current_package_path + [module_name])

    _load_modules([Path(path[0]).name])
