"""Tests relating to the form view mixins."""
from unittest.mock import patch

import pytest
from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from pytest_lazyfixture import lazy_fixture as lazy

from brackets import mixins
from brackets.exceptions import BracketsConfigurationError
from tests.project.models import Article


@pytest.mark.mixin("FormWithUserMixin")
class TestFormWithUserMixin:
    """Tests related to the `FormWithUserMixin`."""

    def test_user_to_form_kwargs(self, form_view, admin_user, rf):
        """User should appear in form's kwargs."""
        request = rf.get("/")
        request.user = admin_user
        view = form_view()
        form_kwargs = view(request=request).get_form_kwargs()
        assert form_kwargs["user"] == admin_user

    def test_user_to_form_wrapped_class(self, form_view, form_class, admin_user, rf):
        """A non-UserFormMixin form has the mixin applied."""
        request = rf.get("/")
        request.user = admin_user
        view = form_view()
        view.form_class = form_class()
        assert issubclass(view(request=request).get_form_class(), mixins.UserFormMixin)

    def test_mro_preserved(self, form_view, form_class, admin_user, rf):
        """A form that already has `UserFormMixin` is not wrapped."""

        class Flag:
            """A flag to indicate that the classes are preserved."""

        request = rf.get("/")
        request.user = admin_user
        view = form_view()
        view.form_class = form_class()
        view.form_class.__bases__ = (Flag, mixins.UserFormMixin, forms.Form)
        assert issubclass(view(request=request).get_form_class(), Flag)


@pytest.mark.parametrize(
    ("form", "view"),
    [
        (lazy("form_class"), lazy("form_view")),
        (lazy("model_form_class"), lazy("model_form_view")),
    ],
)
@pytest.mark.mixin("CSRFExemptMixin")
class TestCSRFExempt:
    """Tests for the CSRFExemptMixin."""

    def test_csrf_exempt(self, form, view, rf):
        """CSRF-exempt views should pass without a CSRF token."""
        request = rf.post("/", data={})
        view = view()
        view.form_class = form()
        view.post = lambda s, r, *a, **k: HttpResponse("django-brackets")
        view.success_url = "/"

        assert view.as_view()(request).status_code == 200


@pytest.mark.mixin("MultipleFormsMixin")
class TestMultipleFormsMixin:
    """Tests related to the MultipleFormsMixin."""

    def test_extra_context(self, form_view, form_class, rf):
        """A view can take extra context."""
        request = rf.get("/")
        view_class = form_view()(
            extra_context={"foo": "bar"},
            form_classes={"one": form_class()},
            request=request,
        )
        assert view_class.get_context_data()["foo"] == "bar"

    def test_missing_form_classes(self, form_view):
        """A view with no instances or initials should fail."""
        view_class = form_view()
        with pytest.raises(ImproperlyConfigured):
            view_class().get_form_classes()

    def test_non_dict_form_classes(self, form_view):
        """A view raises an exception for non-dictionary `form_classes`."""
        view_class = form_view()(form_classes=["foo", "bar"])
        with pytest.raises(ImproperlyConfigured):
            view_class.get_form_classes()

    @pytest.mark.parametrize(
        ("form", "view"),
        [
            (lazy("form_class"), lazy("form_view")),
            (lazy("model_form_class"), lazy("model_form_view")),
        ],
    )
    def test_form_classes(self, form, view):
        """The view should return all prescribed form classes."""
        fv = view()
        fc = form()
        fv.form_classes = {"two": fc, "one": fc}
        assert fv().get_form_classes() == {"one": fc, "two": fc}

    @pytest.mark.parametrize(
        ("form", "view"),
        [
            (lazy("form_class"), lazy("form_view")),
            (lazy("model_form_class"), lazy("model_form_view")),
        ],
    )
    def test_forms_in_context(self, form, view, rf):
        """Forms should appear in the view's context."""
        req = rf.get("/")
        view = view()
        view.form_classes = {"one": form(), "two": form()}
        context = view(request=req).get_context_data()
        assert "one" in context["forms"]
        assert "two" in context["forms"]

    @pytest.mark.parametrize(
        ("form", "view"),
        [
            (lazy("form_class"), lazy("form_view")),
            (lazy("model_form_class"), lazy("model_form_view")),
        ],
    )
    def test_forms_with_initial_values(self, form, view, rf):
        """Initial values provided in the view should show in the form."""
        request = rf.get("/")
        view = view()
        view.form_initial_values = {"one": {"name": "bar"}}
        view.form_classes = {"one": form(), "two": form()}
        context = view(request=request).get_context_data()
        assert context["forms"]["one"].initial == {"name": "bar"}
        assert context["forms"]["two"].initial == {}

    @pytest.mark.parametrize(
        ("form", "view"),
        [
            (lazy("form_class"), lazy("form_view")),
            (lazy("model_form_class"), lazy("model_form_view")),
        ],
    )
    def test_forms_valid(self, form, view, rf):
        """Forms receiving valid data should validate as such."""
        request = rf.post("/", data={"one-title": "foo", "two-slug": 42})
        view = view()
        view.form_classes = {
            "one": form(title=forms.CharField()),
            "two": form(slug=forms.SlugField()),
        }
        view.forms_valid = lambda x: HttpResponse("django-brackets")
        view.forms_invalid = lambda x: HttpResponse("django-braces")
        _view = view(request=request)
        context = _view.get_context_data()
        assert _view.validate_forms()
        assert context["forms"]["one"].is_valid()
        assert context["forms"]["two"].is_valid()
        response = view.as_view()(request)
        assert 100 < response.status_code < 300

    @pytest.mark.parametrize(
        ("view", "method"),
        [
            (lazy("form_view"), "forms_valid"),
            (lazy("form_view"), "forms_invalid"),
            (lazy("model_form_view"), "forms_valid"),
            (lazy("model_form_view"), "forms_invalid"),
        ],
    )
    def test_not_implemented(self, view, method):
        """Views much implement `forms_valid` and `forms_invalid`."""
        view = view()()
        with pytest.raises(NotImplementedError):
            getattr(view, method)()

    @pytest.mark.parametrize(
        "instances", [None, "django-brackets", {"django-braces": "django-brackets"}]
    )
    def test_get_instance_improperly_configured(self, form_view, instances):
        """An improperly configured view raises an exception."""
        view = form_view()(form_instances=instances)
        with pytest.raises(BracketsConfigurationError):
            view.get_instance("django-brackets")

    def test_instance_found(self, form_view):
        """If a view is asked for a provided instance, it should be provided."""
        view = form_view()
        view = view(form_instances={"db": "bd"})
        assert view.get_instance("db") == "bd"

    def test_get_initial_improperly_configured(self, form_view):
        """An improperly configured view raises an exception."""
        view = form_view()(form_initial_values="django-brackets")
        with pytest.raises(BracketsConfigurationError):
            view.get_initial("django-brackets")

    def test_get_initial_keyerror(self, form_view):
        """If the initial doesn't exist, a blank dict is returned."""
        view = form_view()(form_initial_values={"foo": "bar"})
        assert view.get_initial("bar") == {}

    @pytest.mark.django_db()
    def test_instance_in_form_kwargs(self, model_form_view, model_form_class, rf):
        """Instances should appear in ModelForm form kwargs."""
        request = rf.get("/")
        form_class = model_form_class()
        instance = Article.objects.create(title="Foo")
        view = model_form_view()(
            request=request,
            form_classes={"foo": form_class()},
            form_instances={"foo": instance},
        )
        assert view.get_form_kwargs("foo")["instance"] == instance

    @pytest.mark.parametrize(("valid",), [(True,), (False,)])  # noqa: PT006
    @patch(
        "brackets.mixins.MultipleFormsMixin.forms_invalid", return_value=HttpResponse()
    )
    @patch(
        "brackets.mixins.MultipleFormsMixin.forms_valid", return_value=HttpResponse()
    )
    @patch("brackets.mixins.MultipleFormsMixin.validate_forms")
    def test_post(
        self,
        validate_forms,
        forms_valid,
        forms_invalid,
        form_view,
        form_class,
        rf,
        valid,
    ):
        """Valid forms should call `forms_valid` and vice versa."""
        view = form_view()
        view.form_classes = {
            "one": form_class(title=forms.CharField()),
            "two": form_class(slug=forms.SlugField()),
        }
        validate_forms.return_value = valid
        request = rf.post(
            "/", data={"one-title": "django-brackets", "two-slug": "brackets"}
        )
        response = view.as_view()(request)

        assert response.status_code == 200
        validate_forms.assert_called_once()
        forms_valid.assert_called() if valid else forms_valid.assert_not_called()
        forms_invalid.assert_called() if not valid else forms_invalid.assert_not_called()
