"""Authentication and Authorization mixins."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import logout_then_login
from django.core.exceptions import BadRequest, ImproperlyConfigured
from django.utils.timezone import now
from django.views import View

from .redirects import RedirectMixin

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from typing import Optional

    from django.db.models.base import ModelBase

    from . import _A, _K, _StringOrMenu

__all__: list[str] = [
    "PassesTestMixin",
    "PassOrRedirectMixin",
    "SuperuserRequiredMixin",
    "StaffUserRequiredMixin",
    "GroupRequiredMixin",
    "AnonymousRequiredMixin",
    "LoginRequiredMixin",
    "RecentLoginRequiredMixin",
    "PermissionRequiredMixin",
    "SSLRequiredMixin",
]

USER_MODEL: ModelBase = get_user_model()


class PassesTestMixin(View):
    """The view is not dispatched unless a test method passes.

    Executes a test function before `View.dispatch` is called. On failure,
    another method is called to handle whatever comes next.
    """

    dispatch_test: str = ""

    def dispatch(self, request: http.HttpRequest, *args: _A, **kwargs: _K) -> http.HttpResponse:
        """Run the test method and dispatch the view if it passes."""
        test_method: Callable[[], bool] = self.get_test_method()

        if not test_method():
            return self.handle_test_failure()

        return super().dispatch(request, *args, **kwargs)

    def get_test_method(self) -> Callable[[], bool]:
        """Find the method to test the request with.

        Provide a callable object or a string that can be used to
        look up a callable
        """
        _class: str = self.__class__.__name__
        _test: str = self.dispatch_test  # type: ignore
        _missing_error_message: str = (
            f"{_class} is missing the `{_test}` method. "
            f"Define `{_class}.{_test}` or override "
            f"`{_class}.get_dispatch_test."
        )
        _callable_error_message: str = f"{_class}.{_test} must be a callable."
        if not self.dispatch_test or self.dispatch_test is None:
            raise ImproperlyConfigured(_missing_error_message)

        try:
            method: Callable = getattr(self, self.dispatch_test)
        except AttributeError as exc:
            raise ImproperlyConfigured(_missing_error_message) from exc

        if not callable(method) or not method:
            raise ImproperlyConfigured(_callable_error_message)

        return method

    def handle_test_failure(self) -> http.HttpResponse:
        """Test failed, raise an exception or redirect."""
        return http.HttpResponseBadRequest()


class PassOrRedirectMixin(PassesTestMixin, RedirectMixin):
    """Failing requests should be redirected."""

    redirect_url: str = "/"
    redirect_unauthenticated_users: bool = True

    def handle_test_failure(self) -> http.HttpResponse:
        """Redirect a failed test."""
        # redirect unauthenticated users to login
        if (
            not self.request.user or not self.request.user.is_authenticated
        ) and self.redirect_unauthenticated_users:
            return self.redirect()

        return super().handle_test_failure()


class SuperuserRequiredMixin(PassesTestMixin):
    """Require the user to be an authenticated superuser."""

    dispatch_test: str = "test_superuser"

    def test_superuser(self) -> bool:
        """The user must be both authenticated and a superuser."""
        if (user := getattr(self.request, "user", None)) is not None:
            return bool(user.is_authenticated and user.is_superuser)
        return False


class StaffUserRequiredMixin(PassesTestMixin):
    """Require the user to be an authenticated staff user."""

    dispatch_test: str = "test_staffuser"

    def test_staffuser(self) -> bool:
        """The user must be authenticated and `is_staff` must be True."""
        if (user := getattr(self.request, "user", None)) is not None:
            return user.is_authenticated and user.is_staff
        return False


class GroupRequiredMixin(PassesTestMixin):
    """Requires an authenticated user who is also a group member."""

    group_required: Optional[str | list[str]] = None
    dispatch_test: str = "check_groups"

    def get_group_required(self) -> list[str]:
        """Return a list of required groups."""
        if self.group_required is None:
            _class: str = self.__class__.__name__
            _err_msg: str = (
                f"{_class} is missing the `group_required` "
                f"attribute. Define `{_class}.group_required` or"
                f"override `{_class}.get_group_required()."
            )
            raise ImproperlyConfigured(_err_msg)
        if isinstance(self.group_required, str):
            return [self.group_required]
        return self.group_required

    def check_membership(self) -> bool:
        """Check the user's membership in the required groups."""
        return bool(
            set(self.get_group_required()).intersection(
                [group.name for group in self.request.user.groups.all()],
            ),
        )

    def check_groups(self) -> bool:
        """Check that the user is authenticated and a group member."""
        if (user := getattr(self.request, "user", None)) is not None:
            return user.is_authenticated and self.check_membership()
        return False


class AnonymousRequiredMixin(PassesTestMixin):
    """Require the user to be anonymous."""

    dispatch_test: str = "test_anonymous"
    redirect_unauthenticated_users: bool = False

    def test_anonymous(self) -> bool:
        """Accept anonymous users."""
        if (user := getattr(self.request, "user", None)) is not None:
            return not user.is_authenticated
        return True


class LoginRequiredMixin(PassesTestMixin):
    """Require the user to be authenticated."""

    dispatch_test: str = "test_authenticated"

    def test_authenticated(self) -> bool:
        """The user must be authenticated."""
        if (user := getattr(self.request, "user", None)) is not None:
            return user.is_authenticated
        return False


class RecentLoginRequiredMixin(PassesTestMixin):
    """Require the user to be recently authenticated."""

    dispatch_test: str = "test_recent_login"
    max_age: int = 1800  # 30 minutes

    def test_recent_login(self) -> bool:
        """Make sure the user's login is recent enough."""
        if (user := getattr(self.request, "user", None)) is not None:
            return user.is_authenticated and user.last_login > now() - timedelta(
                seconds=self.max_age,
            )
        return False

    def handle_test_failure(self) -> http.HttpResponseRedirect:
        """Logout the user and redirect to login."""
        return logout_then_login(self.request)


class PermissionRequiredMixin(PassesTestMixin):
    """Require a user to have specific permission(s)."""

    permission_required: _StringOrMenu = None
    dispatch_test: str = "check_permissions"

    def get_permission_required(self) -> _Menu:
        """Return a dict of required and optional permissions."""
        if self.permission_required is None:
            _class: str = self.__class__.__name__
            _err_msg: str = (
                f"{_class} is missing the `permission_required` attribute. "
                f"Define `{_class}.permission_required` or "
                f"override `{_class}.get_permission_required()`."
            )
            raise ImproperlyConfigured(_err_msg)
        if isinstance(self.permission_required, str):
            return {"all": [self.permission_required]}
        return self.permission_required

    def check_permissions(self) -> bool:
        """Check user for appropriate permissions."""
        permissions: _Menu = self.get_permission_required()
        _all: list[str] = permissions.get("all", [])
        _any: list[str] = permissions.get("any", [])

        if not getattr(self.request, "user", None):
            return False
        perms_all = self.request.user.has_perms(_all) or []
        perms_any = [self.request.user.has_perm(perm) for perm in _any]

        return any((perms_all, any(perms_any)))


class SSLRequiredMixin(PassesTestMixin):
    """Require the request to be using SSL."""

    dispatch_test: str = "test_ssl"
    redirect_to_ssl: bool = True

    def test_ssl(self) -> bool:
        """Reject non-SSL requests."""
        # SSL isn't usually used/available during testing, so skip it.
        if getattr(settings, "DEBUG", False):
            return True  # pragma: no cover

        return self.request.is_secure()

    def handle_test_failure(self) -> http.HttpResponse | BadRequest:
        """Redirect to the SSL version of the request's URL."""
        if self.redirect_to_ssl:
            current = self.request.build_absolute_uri(self.request.get_full_path())
            secure = current.replace("http://", "https://")
            return http.HttpResponsePermanentRedirect(secure)
        return super().handle_test_failure()
