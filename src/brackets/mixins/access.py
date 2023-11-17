"""Authentication and Authorization mixins."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django import http
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import logout_then_login
from django.utils.timezone import now

from brackets.exceptions import BracketsConfigurationError

from .redirects import RedirectMixin

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable
    from typing import Any

    from django.db.models.base import ModelBase

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


class PassesTestMixin:
    """The view is not dispatched unless a test method passes.

    Executes a test function before `View.dispatch` is called. On failure,
    another method is called to handle whatever comes next.
    """

    dispatch_test: str = ""

    def dispatch(
        self, request: http.HttpRequest, *args: tuple[Any], **kwargs: dict[str, Any]
    ) -> http.HttpResponse:
        """Run the test method and dispatch the view if it passes."""
        test_method: Callable[..., bool] = self.get_test_method()

        if not test_method():
            return self.handle_dispatch_test_failure()

        return super().dispatch(request, *args, **kwargs)

    def get_test_method(self) -> Callable[..., bool]:
        """Find the method to test the request with.

        Provide a callable object or a string that can be used to
        look up a callable
        """
        _class: str = self.__class__.__name__
        _test: str = self.dispatch_test
        _missing_error_message: str = (
            f"{_class} is missing the `{_test}` method. "
            f"Define `{_class}.{_test}` or override "
            f"`{_class}.get_dispatch_test."
        )
        _callable_error_message: str = f"{_class}.{_test} must be a callable."
        if not self.dispatch_test:
            raise BracketsConfigurationError(_missing_error_message)

        try:
            method: Callable[..., bool] = getattr(self, self.dispatch_test)
        except AttributeError as exc:
            raise BracketsConfigurationError(_missing_error_message) from exc

        if not callable(method):
            raise BracketsConfigurationError(_callable_error_message)

        return method

    def handle_dispatch_test_failure(self) -> http.HttpResponse:
        """Test failed, raise an exception or redirect."""
        return http.HttpResponseBadRequest()


class PassOrRedirectMixin(PassesTestMixin, RedirectMixin):
    """Failing requests should be redirected."""

    redirect_url: str = "/"
    redirect_unauthenticated_users: bool = True

    def handle_dispatch_test_failure(self) -> http.HttpResponse:
        """Redirect a failed test."""
        # redirect unauthenticated users to login
        if (
            not self.request.user or not self.request.user.is_authenticated
        ) and self.redirect_unauthenticated_users:
            return self.redirect()

        return super().handle_dispatch_test_failure()


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
            return bool(user.is_authenticated and user.is_staff)
        return False


class GroupRequiredMixin(PassesTestMixin):
    """Requires an authenticated user who is also a group member."""

    group_required: str | list[str] = ""
    dispatch_test: str = "check_groups"

    def get_group_required(self) -> list[str]:
        """Return a list of required groups."""
        if not self.group_required:
            _class: str = self.__class__.__name__
            _err_msg: str = (
                f"{_class} is missing the `group_required` "
                f"attribute. Define `{_class}.group_required` or"
                f"override `{_class}.get_group_required()."
            )
            raise BracketsConfigurationError(_err_msg)
        if isinstance(self.group_required, str):
            return [self.group_required]
        return self.group_required

    def check_membership(self) -> bool:
        """Check the user's membership in the required groups."""
        groups_required: set[str] = set(self.get_group_required())
        user_groups: set[str] = set(
            self.request.user.groups.values_list("name", flat=True)
        )
        return bool(groups_required.intersection(user_groups))

    def check_groups(self) -> bool:
        """Check that the user is authenticated and a group member."""
        if (user := getattr(self.request, "user", None)) is not None:  # type: ignore
            return user.is_authenticated and self.check_membership()
        return False


class AnonymousRequiredMixin(PassesTestMixin):
    """Require the user to be anonymous."""

    dispatch_test: str = "test_anonymous"
    redirect_unauthenticated_users: bool = False

    def test_anonymous(self) -> bool:
        """Accept anonymous users."""
        if (user := getattr(self.request, "user", None)) is not None:  # type: ignore
            return not user.is_authenticated
        return True


class LoginRequiredMixin(PassesTestMixin):
    """Require the user to be authenticated."""

    dispatch_test: str = "test_authenticated"

    def test_authenticated(self) -> bool:
        """The user must be authenticated."""
        if (user := getattr(self.request, "user", None)) is not None:  # type: ignore
            return bool(user.is_authenticated)
        return False


class RecentLoginRequiredMixin(PassesTestMixin):
    """Require the user to be recently authenticated."""

    dispatch_test: str = "check_recent_login"
    max_age: int = 1800  # 30 minutes

    def check_recent_login(self) -> bool:
        """Make sure the user's login is recent enough."""
        if (user := getattr(self.request, "user", None)) is not None:  # type: ignore
            return all(
                [
                    user.is_authenticated,
                    user.last_login > now() - timedelta(seconds=self.max_age),
                ]
            )
        return False

    def handle_dispatch_test_failure(self) -> http.HttpResponseRedirect:
        """Logout the user and redirect to login."""
        return logout_then_login(self.request)


class PermissionRequiredMixin(PassesTestMixin):
    """Require a user to have specific permission(s)."""

    permission_required: str | dict[str, list[str]] = ""
    dispatch_test: str = "check_permissions"

    def get_permission_required(self) -> dict[str, list[str]]:
        """Return a dict of required and optional permissions."""
        if not self.permission_required:
            _class: str = self.__class__.__name__
            _err_msg: str = (
                f"{_class} is missing the `permission_required` attribute. "
                f"Define `{_class}.permission_required` or "
                f"override `{_class}.get_permission_required()`."
            )
            raise BracketsConfigurationError(_err_msg)
        if isinstance(self.permission_required, str):
            return {"all": [self.permission_required]}
        return self.permission_required

    def check_permissions(self) -> bool:
        """Check user for appropriate permissions."""
        permissions: dict[str, list[str]] = self.get_permission_required()
        _all: list[str] = permissions.get("all", [])
        _any: list[str] = permissions.get("any", [])

        if not getattr(self.request, "user", None):  # type: ignore
            return False
        perms_all: list[bool] = self.request.user.has_perms(_all) or []
        perms_any: list[bool] = [self.request.user.has_perm(perm) for perm in _any]

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

        return self.request.is_secure()  # type: ignore

    def handle_dispatch_test_failure(
        self,
    ) -> http.HttpResponse | http.HttpResponseBadRequest:
        """Redirect to the SSL version of the request's URL."""
        if self.redirect_to_ssl:
            current: str = self.request.build_absolute_uri(self.request.get_full_path())
            secure: str = current.replace("http://", "https://")
            return http.HttpResponsePermanentRedirect(secure)
        return super().handle_dispatch_test_failure()
