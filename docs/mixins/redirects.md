---
hide:
- navigation
---
# Redirection Mixins

The mixins in this group are all related to redirecting HTTP requests.

## RedirectMixin

This mixin provides a `redirect` method that can be used to redirect
the request to another URL. You can provide the URL via the `redirect_url`
attribute or by overriding the `get_redirect_url` method.

```py
from brackets.mixins import RedirectMixin

class SeeYaLaterSucker(RedirectMixin, TemplateView):
    redirect_url = "youre/outta/here.html"
```

## RedirectToLoginMixin

This mixin is effectively the `RedirectMixin` with some preset behaviors.
By default, it redirects to the login URL provided by Django, but you can
override this with either the `login_url` attribute or the `get_login_url`
method.

```py
from brackets.mixins import RedirectToLoginMixin

class GetANameBadge(RedirectToLoginMixin, View):
    login_url = "/login"
```
