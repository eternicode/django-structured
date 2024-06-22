from django.db import models

from django_structured.project_utils import load_modules

__all__ = []
load_modules(__path__, globals(), __all__, subclasses_of=models.Model)
