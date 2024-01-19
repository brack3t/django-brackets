"""Mixins related to HTTP requests and responses."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, TypeAlias

from django.http import HttpRequest, HttpResponse
from django.views.generic import View
from django.views.decorators.cache import cache_control, never_cache

from brackets.exceptions import BracketsConfigurationError

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable


__all__ = ["AllVerbsMixin", "HeaderMixin", "CacheControlMixin", "NeverCacheMixin"]

A: TypeAlias = tuple[Any]
K: TypeAlias = dict[str, Any]

class AllVerbsMixin:
    """Handle all HTTP verbs with a single method."""

    all_verb_handler: str = "all"

    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Run all requests through the all_verb_handler method."""
        if not self.all_verb_handler:
            raise BracketsConfigurationError(
                "%s requires the all_verb_handler attribute to be set."
                % self.__class__.__name__
            )

        handler = getattr(self, self.all_verb_handler, self.http_method_not_allowed)
        return handler(request, *args, **kwargs)

    def all(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Handle all requests."""
        raise NotImplementedError


class HeaderMixin:
    """Mixin for easily adding headers to a response."""

    headers: Optional[dict[str, Any]] = None

    def get_headers(self) -> dict[str, Any]:
        """Return a dictionary of headers to add to the response."""
        if self.headers is None:
            return {}

        if not self.headers:
            raise BracketsConfigurationError(
                "%s requires the `headers` attribute to be set."
                % self.__class__.__name__
            )
        return self.headers

    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Add headers to the response."""
        response = super().dispatch(request, *args, **kwargs)
        for key, value in self.get_headers().items():
            response[key] = value
        return response


class CacheControlMixin:
    """Provides a view with cache control options."""

    cache_control_public: Optional[bool] = None
    cache_control_private: Optional[bool] = None
    cache_control_no_cache: Optional[bool] = None
    cache_control_no_store: Optional[bool] = None
    cache_control_no_transform: Optional[bool] = None
    cache_control_must_revalidate: Optional[bool] = None
    cache_control_proxy_revalidate: Optional[bool] = None
    cache_control_max_age: Optional[int] = None
    cache_control_s_maxage: Optional[int] = None

    def __init__(self, **kwargs: dict[str, None | bool | int]) -> None:
        """Set up Cache Control."""
        self.cache_control_public = kwargs.pop("cache_control_public", None)
        self.cache_control_private = kwargs.pop("cache_control_private", None)
        self.cache_control_no_cache = kwargs.pop("cache_control_no_cache", None)
        self.cache_control_no_store = kwargs.pop("cache_control_no_store", None)
        self.cache_control_no_transform = kwargs.pop("cache_control_no_transform", None)
        self.cache_control_must_revalidate = kwargs.pop(
            "cache_control_must_revalidate", None
        )
        self.cache_control_proxy_revalidate = kwargs.pop(
            "cache_control_proxy_revalidate", None
        )
        self.cache_control_max_age = kwargs.pop("cache_control_max_age", None)
        self.cache_control_s_maxage = kwargs.pop("cache_control_s_maxage", None)

        super().__init__(**kwargs)

    @classmethod
    def get_cache_control_options(
        cls: type["CacheControlMixin"],
    ) -> dict[str, bool | int]:
        """Get the view's cache-control options."""
        options: dict[str, bool | int] = {}
        for key, value in cls.__dict__.items():
            if key.startswith("cache_control_") and value is not None:
                options[key.replace("cache_control_", "")] = value
        return options

    @classmethod
    def as_view(cls: type["CacheControlMixin"], **initkwargs: dict[str, Any]) -> View:
        """Add cache control to the view."""
        view: Callable[[View], HttpResponse] = super().as_view(**initkwargs)
        return cache_control(**cls.get_cache_control_options())(view)


class NeverCacheMixin:
    """Prevents a view from being cached."""

    @classmethod
    def as_view(cls: type["NeverCacheMixin"], **initkwargs: dict[str, Any]) -> View:
        """Wrap the view with never_cache."""
        view: Callable[[View], HttpResponse] = super().as_view(**initkwargs)
        return never_cache(view)
