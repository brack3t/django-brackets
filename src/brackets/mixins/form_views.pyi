from typing import Any, Optional, Protocol, Type

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse

from . import CanDispatch, HasContext, HasHttpMethods, HasRequest

class HasForm(Protocol):
    form_class: type[forms.Form]
    form_kwargs: dict[str, Any]
    def get_form_class(self) -> type[forms.Form]: ...
    def get_form_kwargs(self) -> dict[str, Any]: ...

class FormWithUserMixin(HasRequest, HasForm, CanDispatch):
    form_class: Type[forms.Form]
    form_kwargs: dict[str, Any]
    request: HttpRequest
    def get_form_kwargs(self) -> dict[str, Any]: ...
    def get_form_class(self) -> Type[forms.Form]: ...

class CSRFExemptMixin:
    def dispatch(
        self,
        request: HttpRequest,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> HttpResponse: ...

CsrfExemptMixin = CSRFExemptMixin

class MultipleFormsMixin(HasContext, HasHttpMethods):
    extra_context: Optional[dict[str, Any]] = None
    form_classes: dict[str, forms.Form]
    form_initial_values: dict[str, dict[str, Any]]
    form_instances: dict[str, models.Model]
    get_form: type[forms.Form]
    def forms_valid(self) -> HttpResponse: ...
    def forms_invalid(self) -> HttpResponse: ...
    def get_form_classes(self) -> list[forms.Form]: ...
    def get_forms(self) -> dict[str, forms.Form]: ...
    def get_form_kwargs(self, name: str) -> dict[str, Any]: ...
    def get_instances(self) -> dict[str, models.Model]: ...
    def validate_forms(self) -> bool: ...
