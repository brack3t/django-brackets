from collections.abc import Callable
from typing import Any

from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    StreamingHttpResponse,
)
from django.views.generic.base import View

from .redirects import RedirectMixin

class PassesTestMixin(View):
    dispatch_test: str
    request: HttpRequest
    def dispatch(
        self, request: HttpRequest, *args: tuple[Any, ...], **kwargs: dict[Any, Any]
    ) -> HttpResponse: ...
    def get_test_method(self) -> Callable[[Any], bool]: ...
    def handle_test_failure(self) -> HttpResponse: ...

class PassOrRedirectMixin(PassesTestMixin, RedirectMixin):
    raise_exception: bool | Exception | Callable[
        [HttpRequest], HttpResponse | StreamingHttpResponse
    ]
    redirect_unauthenticated_users: bool
    redirect_url: str
    request: HttpRequest
    def handle_test_failure(self) -> HttpResponse: ...

class SuperuserRequiredMixin(PassesTestMixin):
    dispatch_test: str
    request: HttpRequest
    def test_superuser(self) -> bool: ...

class StaffUserRequiredMixin(PassesTestMixin):
    dispatch_test: str
    request: HttpRequest
    def test_staffuser(self) -> bool: ...

class GroupRequiredMixin(PassesTestMixin):
    group_required: str | list[str]
    dispatch_test: str
    def get_group_required(self) -> list[str]: ...
    def check_membership(self) -> bool: ...
    def check_groups(self) -> bool: ...

class AnonymousRequiredMixin(PassesTestMixin):
    dispatch_test: str
    redirect_unauthenticated_users: bool
    def test_anonymous(self) -> bool: ...

class LoginRequiredMixin(PassesTestMixin):
    dispatch_test: str
    def test_authenticated(self) -> bool: ...

class RecentLoginRequiredMixin(PassesTestMixin):
    dispatch_test: str
    max_age: int
    def test_recent_login(self) -> bool: ...
    def handle_test_failure(self) -> HttpResponseRedirect: ...

class PermissionRequiredMixin(PassesTestMixin):
    permission_required: str | dict[str, list[str]]
    dispatch_test: str
    def get_permission_required(self) -> dict[str, list[str]]: ...
    def check_permissions(self) -> bool: ...

class SSLRequiredMixin(PassesTestMixin):
    dispatch_test: str
    redirect_to_ssl: bool
    def test_ssl(self) -> bool: ...
    def handle_test_failure(self) -> HttpResponse | HttpResponseBadRequest: ...
