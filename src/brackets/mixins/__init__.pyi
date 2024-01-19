from typing import Any, ClassVar, Protocol

from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic.base import ContextMixin

from .access import *
from .form_views import *
from .forms import *
from .http import *
from .queries import *
from .redirects import *
from .rest_framework import *

class CanQuery(Protocol):  # The concept of a view that can query.
    queryset: QuerySet[Model]
    def get_queryset(self: CanQuery) -> QuerySet[Model]: ...

class CanDispatch(Protocol):  # The concept of a view that can dispatch requests.
    def dispatch(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...

class _ContextProtocol(Protocol):
    context: ClassVar[dict[str, Any]]

    def get_context_data(self, **kwargs: dict[Any, Any]) -> dict[str, Any]: ...

class HasContext(_ContextProtocol, ContextMixin):  # The concept of `context`.
    context: ClassVar[dict[str, Any]]

    def get_context_data(self, **kwargs: dict[Any, Any]) -> dict[str, Any]: ...

class HasRequest(Protocol):  # The existence of `self.request`.
    request: HttpRequest

class HasContent(Protocol):  # The concept of `content_type`.
    content_type: str

    def get_content_type(self) -> str: ...

class HasHttpMethods(Protocol):  # The concept of handling HTTP verbs.
    def delete(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def get(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def head(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def options(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def patch(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def post(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def put(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...
    def trace(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> HttpResponse: ...

class BaseView(
    CanDispatch, _ContextProtocol, HasRequest, HasContent, HasHttpMethods, Protocol
):  # The concept of a Django view.
    def __init__(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None: ...
