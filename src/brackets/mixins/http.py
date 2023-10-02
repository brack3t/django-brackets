"""Mixins related to HTTP requests and responses."""

from __future__ import annotations

from typing import Any, TypeAlias

from django.views.decorators.cache import cache_control, never_cache

from brackets.exceptions import BracketsConfigurationError

if typing.TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

    from django.http import HttpRequest, HttpResponse
    from django.http.response import HttpResponseBase

__all__ = ["AllVerbsMixin", "HeaderMixin", "CacheControlMixin", "NeverCacheMixin"]

A: TypeAlias = tuple[Any, ...]
K: TypeAlias = dict[str, Any]


class AllVerbsMixin:
    """Handle all HTTP verbs with a single method."""

    all_verb_handler: str = "all"

    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Run all requests through the all_verb_handler method."""
        if not self.all_verb_handler:
            err = (
                f"{self.__class__.__name__} requires the all_verb_handler "  # fmt: skip
                "attribute to be set."
            )
            raise BracketsConfigurationError(err)

        handler = getattr(self, self.all_verb_handler, self.http_method_not_allowed)
        return handler(request, *args, **kwargs)

    def all(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Handle all requests."""
        raise NotImplementedError


class HeaderMixin:
    """Mixin for easily adding headers to a response."""

    headers: dict[str, Any] = {}

    def get_headers(self) -> dict[str, Any]:
        """Return a dictionary of headers to add to the response."""
        return self.headers

    def dispatch(self, request: HttpRequest, *args: A, **kwargs: K) -> HttpResponse:
        """Add headers to the response."""
        response = super().dispatch(request, *args, **kwargs)
        for key, value in self.get_headers().items():
            response[key] = value
        return response


class CacheControlMixin:
    """Provides a view with cache control options."""

    cache_control_public = None
    cache_control_private = None
    cache_control_no_cache = None
    cache_control_no_store = None
    cache_control_no_transform = None
    cache_control_must_revalidate = None
    cache_control_proxy_revalidate = None
    cache_control_max_age = None
    cache_control_s_maxage = None

    @classmethod
    def get_cache_control_options(cls) -> dict[str, bool | int]:
        """Get the view's cache-control options."""
        options: dict[str, bool | int] = {}
        for key, value in cls.__dict__.items():
            if key.startswith("cache_control_") and value is not None:
                options[key.replace("cache_control_", "")] = value
        return options

    @classmethod
    def as_view(cls, **initkwargs: dict[str, typing.Any]):
        """Add cache control to the view."""
        view = super().as_view(**initkwargs)
        return cache_control(**cls.get_cache_control_options())(view)


class NeverCacheMixin:
    """Prevents a view from being cached."""

    @classmethod
    def as_view(cls, **initkwargs: dict[str, typing.Any]):
        """Wrap the view with never_cache."""
        view = super().as_view(**initkwargs)
        return never_cache(view)
