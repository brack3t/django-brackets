from typing import Any, Callable, ClassVar, Optional, TypeAlias

from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.views.generic.base import View

A: TypeAlias = tuple[Any, ...]
K: TypeAlias = dict[str, Any]

class AllVerbsMixin:
    all_verb_handler: str
    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse: ...
    def all(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse: ...

class HeaderMixin:
    headers: ClassVar[dict[str, Any]]
    def get_headers(self) -> dict[str, Any]: ...
    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse: ...

class CacheControlMixin(View):
    cache_control_public: Optional[bool]
    cache_control_private: Optional[bool]
    cache_control_no_cache: Optional[bool]
    cache_control_no_store: Optional[bool]
    cache_control_no_transform: Optional[bool]
    cache_control_must_revalidate: Optional[bool]
    cache_control_proxy_revalidate: Optional[bool]
    cache_control_max_age: Optional[int]
    cache_control_s_maxage: Optional[int]
    @classmethod
    def get_cache_control_options(
        cls: type[CacheControlMixin],
    ) -> dict[str, bool | int]: ...
    @classmethod
    def as_view(
        cls: type[CacheControlMixin],
        **initkwargs: K,
    ) -> Callable[..., HttpResponseBase]: ...

class NeverCacheMixin:
    @classmethod
    def as_view(cls: type[NeverCacheMixin], **initkwargs: K) -> HttpResponse: ...
