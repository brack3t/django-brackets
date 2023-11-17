"""Tests related to the HTTP mixins."""
import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.views.generic import View

from brackets.exceptions import BracketsConfigurationError


@pytest.fixture()
def all_verbs_view(mixin_view):
    """Fixture for a view with the AllVerbsMixin."""

    def view(**kwargs):
        """Create a view that responds 'OK' to all HTTP verbs."""
        out_class: type[View] = type(
            "AllVerbsView",
            (mixin_view(all=lambda s, r: HttpResponse("OK")), View),
            kwargs,
        )
        return out_class

    return view


@pytest.mark.mixin("AllVerbsMixin")
class TestAllVerbs:
    """Tests related to the AllVerbsMixin."""

    @pytest.mark.parametrize(
        "verb",
        ["get", "post", "put", "patch", "delete", "head", "options", "trace"],
    )
    def test_verbs(self, verb, all_verbs_view, rf):
        """All HTTP verbs should be handled by the mixin's method."""
        request = getattr(rf, verb)("/")
        response = all_verbs_view().as_view()(request)
        assert response.status_code == 200

    def test_undefined_handler(self, mixin_view, rf):
        """If the handler is not defined, raise an exception."""
        with pytest.raises(NotImplementedError):
            mixin_view().as_view()(rf.get("/"))

    def test_missing_handler(self, all_verbs_view, rf):
        """If the handler is None, raise an exception."""
        view = all_verbs_view()
        view.all_verb_handler = None
        with pytest.raises(ImproperlyConfigured):
            view.as_view()(rf.get("/"))


@pytest.fixture()
def cache_view(mixin_view):
    """Fixture for a view with the CacheControlMixin."""

    def view(**kwargs):
        """Create a cache-controlled view."""
        out_class: type[View] = type(
            "CacheControlView",
            (
                mixin_view(),
                View,
            ),
            kwargs,
        )
        return out_class

    return view


@pytest.mark.mixin("CacheControlMixin")
class TestCacheControl:
    """Tests related to the CacheControlMixin."""

    def test_cache_control(self, cache_view, rf):
        """The CacheControlMixin should apply cache control headers."""
        response = cache_view(
            cache_control_max_age=120,
            cache_control_no_cache=120,
            get=lambda s, r: HttpResponse("OK"),
        ).as_view()(rf.get("/"))
        assert "max-age=120" in response["Cache-Control"]
        assert "no-cache" in response["Cache-Control"]


@pytest.mark.mixin("HeaderMixin")
class TestHeader:
    """Tests related to the HeaderMixin."""

    def test_headers(self, mixin_view, rf):
        """Provided headers should be added to the response."""
        view = mixin_view(
            headers={"X-Test": "YES"},
        )
        response = view.as_view()(rf.get("/"))
        assert response["X-Test"] == "YES"

    def test_headers_unset(self, mixin_view, rf):
        """If no headers are provided, nothing should be added."""
        view = mixin_view()
        response = view.as_view()(rf.get("/"))

        with pytest.raises(KeyError):
            response["X-Test"]

    def test_headers_empty(self, mixin_view, rf):
        """If no headers are provided, nothing should be added."""
        view = mixin_view(headers={})
        with pytest.raises(BracketsConfigurationError):
            view.as_view()(rf.get("/"))

    def test_request_headers(self, mixin_view, rf):
        """Headers coming in on a request shouldn't come out on a response."""
        _resp = HttpResponse("OK", headers={"Age": 120})
        view = mixin_view(headers={"X-Test": "YES"}, get=lambda s, r: _resp)
        response = view.as_view()(rf.get("/"))
        assert response["X-Test"] == "YES"
        with pytest.raises(KeyError):
            response["Age"]


@pytest.mark.mixin("NeverCacheMixin")
class TestNeverCache:
    """Tests related to the NeverCacheMixin."""

    def test_never_cache(self, mixin_view, rf):
        """A NeverCacheMixin view should include headers to avoid being cached."""
        response = mixin_view().as_view()(rf.get("/"))
        assert (
            response["Cache-Control"]
            == "max-age=0, no-cache, no-store, must-revalidate, private"
        )
