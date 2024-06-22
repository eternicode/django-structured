import pkgutil


def load_models():
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        loader.find_spec(module_name).loader.load_module(module_name)


load_models()
del load_models
