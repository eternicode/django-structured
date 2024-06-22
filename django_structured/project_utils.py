import pkgutil
from typing import Dict, Iterable, List


def load_modules(
    path,
    globals_dict: Dict | None = None,
    all_names: List | None = None,
    *,
    recursive: bool = False,
    error_on_globals_conflict: bool = True,
    subclasses_of: type | Iterable[type] | None = None,
    __current_path: str | None = None,
) -> None:
    """
    For use in a package's __init__ module, executes import on all modules in
    the package.

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

        __current_path (str): Used internally for recursion. Don't use.
    """
    __base_path = __current_path

    for loader, module_name, is_pkg in pkgutil.iter_modules(path):
        module = loader.find_spec(module_name).loader.load_module(module_name)

        if __base_path is None:
            __current_path = module_name
        else:
            __current_path = f"{__base_path}.{module_name}"

        if globals_dict is not None or all_names is not None:
            for name in dir(module):
                # All modules have native dunders, plus dunders are generally
                # considered Very Private
                if name.startswith("__") and name.endswith("__"):
                    continue

                obj = getattr(module, name)

                if subclasses_of is not None and not issubclass(obj, subclasses_of):
                    continue

                if globals_dict is not None:
                    if name in globals_dict and error_on_globals_conflict:
                        raise NameError(
                            f"Duplicate name '{name}' in '{__current_path}' "
                            f"and '{globals_dict[name].__module__}'"
                        )
                    globals_dict[name] = obj

                if all_names is not None:
                    all_names.append(name)

        if is_pkg and recursive:
            load_modules(
                module.__path__,
                globals_dict,
                all_names,
                recursive=True,
                error_on_globals_conflict=error_on_globals_conflict,
                subclasses_of=subclasses_of,
                __current_path=__current_path,
            )
