from __future__ import annotations

from django import forms
from django.db import models
from django.http import HttpRequest, HttpResponse

from typing import *

from tests.conftest import form_class

from . import CanDispatch, HasContext, A, K, HasHttpMethods, HasRequest


class HasForm(Protocol):
    form_class: type[forms.Form]
    form_kwargs: K
    def get_form_class(self) -> type[forms.Form]: ...
    def get_form_kwargs(self) -> dict[Any, Any]: ...

class FormWithUserMixin(HasRequest, HasForm, CanDispatch):
    form_class; Type[forms.Form]
    form_kwargs: K
    request: HttpRequest
    def get_form_kwargs(self) -> dict[Any, Any]: ...
    def get_form_class(self) -> Type[forms.Form]: ...

class CSRFExemptMixin:
    def dispatch(
        self,
        request: HttpRequest,
        *args: A,
        **kwargs: K,
    ) -> HttpResponse: ...

CsrfExemptMixin = CSRFExemptMixin

class MultipleFormsMixin(HasContext, HasHttpMethods):
    context: K
    form_classes: dict[str, forms.Form]
    initial: K
    get_form: type[forms.Form]
    def __init__(self, *args: A, **kwargs: K) -> None: ...
    def get_form_classes(self) -> list[forms.Form]: ...
    def get_forms(self) -> dict[str, forms.Form]: ...
    def get_form_kwargs(self, name: str) -> K: ...
    def validate_forms(self) -> bool: ...
    def forms_valid(self) -> HttpResponse: ...
    def forms_invalid(self) -> HttpResponse: ...

class MultipleModelFormsMixin(MultipleFormsMixin):
    instances: dict[str, models.Model]
    def get_instances(self) -> dict[str, models.Model]: ...
    def get_form_kwargs(self, name: str) -> K: ...
