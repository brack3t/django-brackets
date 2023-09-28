"""Exceptions for django-brackets mixins."""
from django.core.exceptions import ImproperlyConfigured


class BracketsConfigurationError(ImproperlyConfigured):
    """Raised when a django-brackets mixin is not configured correctly."""
