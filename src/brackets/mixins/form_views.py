"""Mixins relating to forms, model forms, and form views."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from django import forms
from django.forms.forms import BaseForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin

from brackets.exceptions import BracketsConfigurationError
from brackets.mixins.forms import UserFormMixin

if TYPE_CHECKING:
    from typing import Mapping, Sequence

    from django.db import models
    from django.http import HttpRequest, HttpResponse

__all__ = [
    "FormWithUserMixin",
    "CSRFExemptMixin",
    "MultipleFormsMixin",
]


class FormWithUserMixin(FormMixin):
    """Automatically provide request.user to the form's kwargs."""

    def get_form_kwargs(self) -> dict[str, Any]:
        """Inject the request.user into the form's kwargs."""
        kwargs: dict[str, Any] = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs

    def get_form_class(self) -> type[UserFormMixin]:
        """Get the form class or wrap it with UserFormMixin."""
        form_class: type["FormWithUserMixin"] = super().get_form_class()
        if issubclass(form_class, UserFormMixin):
            return form_class

        class FormWithUser(UserFormMixin, form_class):
            __doc__: str = form_class.__doc__

        return FormWithUser


class CSRFExemptMixin:
    """Exempts the view from CSRF requirements."""

    @method_decorator(csrf_exempt)
    def dispatch(
        self, request: HttpRequest, *args: Sequence[Any], **kwargs: Mapping[str, Any]
    ) -> HttpResponse:
        """Dispatch the exempted request."""
        return super().dispatch(request, *args, **kwargs)


CsrfExemptMixin = CSRFExemptMixin


class MultipleFormsMixin(FormMixin):
    """Provides a view with the ability to handle multiple Forms."""

    form_classes: Optional[Mapping[str, type[forms.BaseForm]]] = None
    form_initial_values: Optional[Mapping[str, Mapping[str, Any]]] = None
    form_instances: Optional[Mapping[str, models.Model]] = None

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        """Add the forms to the view context."""
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        kwargs["forms"] = self.get_forms()
        return kwargs

    def get_form_classes(self) -> Mapping[str, type[forms.BaseForm]]:
        """Get the form classes to use in this view."""
        _class: str = self.__class__.__name__
        if not self.form_classes:
            _err_msg = (
                f"{_class} is missing a form_classes attribute. "
                f"Define `{_class}.form_classes`, or override "
                f"`{_class}.get_form_classes()`."
            )
            raise BracketsConfigurationError(_err_msg)

        if not isinstance(self.form_classes, dict):
            _err_msg = f"`{_class}.form_classes` must be a dict."
            raise BracketsConfigurationError(_err_msg)

        return self.form_classes

    def get_forms(self) -> dict[str, forms.BaseForm]:
        """Instantiate the forms with their kwargs."""
        forms: dict[str, forms.BaseForm] = {}
        for name, form_class in self.get_form_classes().items():
            forms[name] = form_class(**self.get_form_kwargs(name))
        return forms

    def get_instance(self, name: str) -> models.Model:
        """Connect instances to forms."""
        _class = self.__class__.__name__
        if not self.form_instances:
            _err_msg = (
                f"{_class} is missing a `form_instances` attribute."
                f"Define `{_class}.form_instances`, or override "
                f"`{_class}.get_instances`."
            )
            raise BracketsConfigurationError(_err_msg)

        if not isinstance(self.form_instances, dict):
            _err_msg = f"`{_class}.form_instances` must be a dictionary."
            raise BracketsConfigurationError(_err_msg)

        try:
            instance = self.form_instances[name]
        except (KeyError, ValueError) as exc:
            _err_msg = f"`{name}` is not an available instance."
            raise BracketsConfigurationError(_err_msg) from exc
        else:
            return instance

    def get_initial(self, name: str) -> dict[str, Any]:  # type: ignore
        """Connect instances to forms."""
        if self.form_initial_values is None:
            return {}

        _class = self.__class__.__name__
        if not self.form_initial_values or isinstance(self.form_initial_values, str):
            _err_msg = (
                f"{_class} is missing a `form_initial_values` attribute."
                f"Define `{_class}.form_initial_values`, or override "
                f"`{_class}.get_initial`."
            )
            raise BracketsConfigurationError(_err_msg)

        try:
            initial: Any = self.form_initial_values[name]
        except (TypeError, KeyError):
            return {}
        else:
            return initial

    def get_form_kwargs(self, name: str) -> dict[str, Any]:  # type: ignore
        """Add common kwargs to the form."""
        kwargs: dict[str, Any] = {
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

    def post(
        self, request: HttpRequest, *args: Sequence[Any], **kwargs: Mapping[str, Any]
    ) -> HttpResponse:
        """Process POST requests: validate and run appropriate handler."""
        if self.validate_forms():
            return self.forms_valid()
        return self.forms_invalid()

    def put(
        self, request: HttpRequest, *args: Sequence[Any], **kwargs: Mapping[str, Any]
    ) -> HttpResponse:
        """Process PUT requests."""
        raise NotImplementedError

    def patch(
        self, request: HttpRequest, *args: Sequence[Any], **kwargs: Mapping[str, Any]
    ) -> HttpResponse:
        """Process PATCH requests."""
        raise NotImplementedError
