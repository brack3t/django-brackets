---
hide:
- navigation
---

# HTTP mixins

The HTTP mixins in `django-brackets` are meant to control the handling
of HTTP beyond what Django already does in `dispatch`.

## AllVerbsMixin

The `AllVerbsMixin` allows you to create a view that responds with
a single method, regardless of the HTTP verb (`GET`, `PUT`, etc) used in the request.

```py
from brackets.mixins import AllVerbsMixin

class YouGetGET(AllVerbsMixin, TemplateView):
    def all(self, request, *args, **kwargs):
        return HttpResponse("Coming Soon")
```

All requests for this view will receive the text "Coming Soon".

## HeaderMixin

The `HeaderMixin` aims to make it easier to control arbitrary headers in
a view's responses. You can provide the headers statically as the `headers`
attribute or programmatically via `get_headers`.

```py
from brackets.mixins import HeaderMixin

class SpecialHeaderMessage(HeaderMixin, TemplateView):
    headers = {"X-WITH-LOVE": True}
```

## CacheControlMixin

Controlling the caching of a response can be a complicated task. This
mixin removes a lot of that complexity and makes cache control very
customizable.

```py
from brackets.mixins import CacheControlMixin

class AgesLikeWine(CacheControlMixin, TemplateView):
    cache_control_max_age = 1_000_000_000
```

You can set the following attributes to control cache for your view:

- `cache_control_public`
- `cache_control_private`
- `cache_control_no_cache`
- `cache_control_no_store`
- `cache_control_no_transform`
- `cache_control_must_revalidate`
- `cache_control_proxy_revalidate`
- `cache_control_max_age`
- `cache_control_s_maxage`

You can read more about caching and what these options relate to
[here, in the Django documentation][django docs].

## NeverCacheMixin

Similar to the `CacheControlMixin`, the `NeverCacheMixin` marks a view as
being uncacheable. This is particularly useful on one-time-use pages.

```py
from brackets.mixins import NeverCacheMixin

class GingerbreadMan(NeverCacheMixin, TemplateView): ...

[django docs]: https://docs.djangoproject.com/en/stable/topics/cache/#controlling-cache-using-other-headers
