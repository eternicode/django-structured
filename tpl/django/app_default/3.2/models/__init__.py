import pkgutil

from django.db import models

__all__ = []


def load_models():
    _globals = globals()
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        module = loader.find_spec(module_name).loader.load_module(module_name)
        # TODO: Just need to load modules, not import classes into init
        # for name in dir(module):
        #     obj = getattr(module, name, None)
        #     if isinstance(obj, models.Model):
        #         if name in _globals:
        #             raise ImportError(
        #                 f"Duplicate Model named '{name}' in '{module_name}' "
        #                 f"and '{_globals[name].__module__}'"
        #             )
        #         _globals[name] = obj
        #         __all__.append(name)


load_models()
del load_models
