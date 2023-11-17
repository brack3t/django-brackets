"""Mixins that redirect requests."""

from __future__ import annotations

from django import http
from django.conf import settings
from django.contrib.auth.views import redirect_to_login

from brackets.exceptions import BracketsConfigurationError

__all__ = [
    "RedirectMixin",
    "RedirectToLoginMixin",
]


class RedirectMixin:
    """Mixin to simplify redirecting a request.

    This mixin is largely for internal use. You are
    probably looking for Django's `RedirectView`.
    """

    redirect_url: str = ""

    def redirect(self) -> http.HttpResponseRedirect:
        """Generate a redirect for the login URL."""
        return http.HttpResponseRedirect(self.get_redirect_url())

    def get_redirect_url(self) -> str:
        """Get the URL to redirect to."""
        url = getattr(self, "redirect_url", None)
        if not url:
            _class = self.__class__.__name__
            _err_msg = (
                f"{_class} is missing the `redirect_url` attribute. "
                f"Define `{_class}.redirect_url` or override "
                f"`{_class}.get_redirect_url`."
            )
            raise BracketsConfigurationError(_err_msg)
        return self.redirect_url


class RedirectToLoginMixin:
    """Redirect failed requests to `LOGIN_URL`."""

    login_url: str = ""

    def get_login_url(self) -> str:
        """Return the URL for the login page."""
        if not self.login_url:
            try:
                self.login_url = settings.LOGIN_URL
            except AttributeError as exc:
                _class = self.__class__.__name__
                _err_msg = (
                    f"{_class} is missing the `login_url` attribute. "
                    f"Define `{_class}.login_url` or `settings.LOGIN_URL`."
                    f"Alternatively, override `{_class}.get_login_url`."
                )
                raise BracketsConfigurationError(_err_msg) from exc
        return self.login_url

    def redirect(self) -> http.HttpResponseRedirect:
        """Generate a redirect for the login URL."""
        return redirect_to_login(self.request.get_full_path(), self.get_login_url())
