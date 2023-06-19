"""Mixins relating to forms, model forms, and form views."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from brackets.mixins.forms import UserFormMixin

if TYPE_CHECKING:
    from typing import Any, Optional

    from django.db import models
    from django.http import HttpRequest, HttpResponse

__all__ = [
    "FormWithUserMixin",
    "CSRFExemptMixin",
    "MultipleFormsMixin",
]


class FormWithUserMixin:
    """Automatically provide request.user to the form's kwargs."""

    def get_form_kwargs(self) -> dict:
        """Inject the request.user into the form's kwargs."""
        kwargs: dict[Any, Any] = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_form_class(self) -> type[forms.Form]:
        """Get the form class or wrap it with UserFormMixin."""
        form_class: type[forms.Form] = super().get_form_class()
        if issubclass(form_class, UserFormMixin):
            return form_class

        class FormWithUser(UserFormMixin, form_class):
            __doc__: str = form_class.__doc__

        return FormWithUser


class CSRFExemptMixin:
    """Exempts the view from CSRF requirements."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Dispatch the exempted request."""
        return super().dispatch(request, *args, **kwargs)


CsrfExemptMixin = CSRFExemptMixin


class MultipleFormsMixin:
    """Provides a view with the ability to handle multiple Forms."""

    form_classes: dict[str, forms.Form] = None
    form_initial_values: dict[str, dict] = {}
    form_instances: dict[str, models.Model] = None

    def __init__(self, *args, **kwargs) -> None:
        """Alias get_forms to get_form for backwards compatibility."""
        super().__init__(*args, **kwargs)
        self.get_form = self.get_forms

    def get_context_data(self, **kwargs) -> dict:
        """Add the forms to the view context."""
        context = super().get_context_data(**kwargs)
        context["forms"] = self.get_forms()
        return context

    def get_form_classes(self) -> list:
        """Get the form classes to use in this view."""
        _class = self.__class__.__name__
        if self.form_classes is None:
            _err_msg = (
                f"{_class} is missing a form_classes attribute. "
                f"Define `{_class}.form_classes`, or override "
                f"`{_class}.get_form_classes()`."
            )
            raise ImproperlyConfigured(_err_msg)

        if not isinstance(self.form_classes, dict):
            _err_msg = f"`{_class}.form_classes` must be a dict."
            raise ImproperlyConfigured(_err_msg)

        return self.form_classes

    def get_forms(self) -> dict[str, forms.Form]:
        """Instantiate the forms with their kwargs."""
        _forms = {}
        for name, form_class in self.get_form_classes().items():
            _forms[name] = form_class(**self.get_form_kwargs(name))
        return _forms

    def get_instance(self, name: str) -> Optional[models.Model]:
        """Connect instances to forms."""
        _class = self.__class__.__name__
        if self.form_instances is None:
            _err_msg = (
                f"{_class} is missing a `form_instances` attribute."
                f"Define `{_class}.form_instances`, or override "
                f"`{_class}.get_instances`."
            )
            raise ImproperlyConfigured(_err_msg)

        if not isinstance(self.form_instances, dict):
            _err_msg = f"`{_class}.form_instances` must be a dictionary."
            raise ImproperlyConfigured(_err_msg)

        try:
            instance = self.form_instances[name]
        except (KeyError, ValueError) as exc:
            _err_msg = f"`{name}` is not an available instance."
            raise ImproperlyConfigured(_err_msg) from exc
        else:
            return instance

    def get_initial(self, name: str) -> Optional[dict[str, Any]]:
        """Connect instances to forms."""
        _class = self.__class__.__name__
        if self.form_initial_values is None:
            _err_msg = (
                f"{_class} is missing a `form_initial_values` attribute."
                f"Define `{_class}.form_initial_values`, or override "
                f"`{_class}.get_initial`."
            )
            raise ImproperlyConfigured(_err_msg)

        if not isinstance(self.form_initial_values, dict):
            _err_msg = f"`{_class}.form_initial_values` must be a dictionary."
            raise ImproperlyConfigured(_err_msg)

        try:
            initial = self.form_initial_values[name]
        except KeyError:
            return {}
        else:
            return initial

    def get_form_kwargs(self, name: str) -> dict[str, Any]:
        """Add common kwargs to the form."""
        kwargs = {
            "prefix": name,  # all forms get a prefix
        }

        kwargs["initial"] = self.get_initial(name)  # use the form's initial data

        form_class = self.get_form_classes()[name].__class__
        if issubclass(form_class, forms.ModelForm):
            kwargs["instance"] = self.get_instance(name)  # use the form's instance

        if self.request.method in {"POST", "PUT", "PATCH"}:
            # Attach the request's POST data and any files to the form
            kwargs["data"] = self.request.POST
            kwargs["files"] = self.request.FILES

        return kwargs

    def validate_forms(self) -> bool:
        """Validate all forms using their own .is_valid() method."""
        _forms = self.get_forms()
        return all(f.is_valid() for f in _forms.values())

    def forms_valid(self) -> HttpResponse:
        """Handle all forms being valid."""
        raise NotImplementedError

    def forms_invalid(self) -> HttpResponse:
        """Handle any form being invalid."""
        raise NotImplementedError

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process POST requests: validate and run appropriate handler."""
        if self.validate_forms():
            return self.forms_valid()
        return self.forms_invalid()

    def put(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process PUT requests."""
        raise NotImplementedError

    def patch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Process PATCH requests."""
        raise NotImplementedError
