from django import http

class RedirectMixin:
    redirect_url: str
    request: http.HttpRequest
    def redirect(self) -> http.HttpResponseRedirect: ...
    def get_redirect_url(self) -> str: ...

class RedirectToLoginMixin(RedirectMixin):
    login_url: str
    request: http.HttpRequest
    def get_login_url(self) -> str: ...
    def redirect(self) -> http.HttpResponseRedirect: ...
