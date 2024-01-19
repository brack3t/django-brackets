"""Provides fixture for django-brackets testing."""
from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, ClassVar, Mapping, TypeVar

import pytest
from django.forms import Form, ModelForm
from django.http import HttpResponse
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseFormView, ModelFormMixin
from django.views.generic.list import MultipleObjectMixin

from .project.models import Article

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, TypeVar

    from django.db import models

    K = Mapping[str, Any]


@pytest.mark.django_db()
@pytest.fixture()
def user(django_user_model: type[models.Model]) -> Callable[[K], models.Model]:
    """Provide a generic user fixture for tests."""

    def _user(**kwargs: dict[str, Any]) -> models.Model:
        """Generate a customizable user."""
        defaults: dict[str, str] = {"username": "test", "password": "Test1234"}
        defaults.update(kwargs)
        user: models.Model = django_user_model.objects.create(**defaults)
        return user

    return _user


@pytest.fixture(name="mixin_view")
def mixin_view_factory(request: pytest.FixtureRequest) -> Callable[[K], type[View]]:
    """Combine a mixin and View for a test."""
    mixin_request = request.node.get_closest_marker("mixin")
    if not mixin_request:
        pytest.fail("No mixin marker found")
    mixins = import_module(".mixins", "brackets")
    mixin_name = mixin_request.args[0]
    mixin_class = getattr(mixins, mixin_name)

    def mixin_view(**kwargs: dict[str, HttpResponse]) -> type[View]:
        """Mixed-in view generator."""
        default_functions: dict = {
            "get": lambda s, r, *a, **k: HttpResponse("django-brackets"),
        }
        kwargs.update(**default_functions)
        _name = f"{mixin_class.__name__}FixtureView"
        return type(_name, (mixin_class, View), kwargs)

    return mixin_view


@pytest.fixture(name="single_object_view")
def single_object_view_factory(
    mixin_view: Callable,
) -> Callable[[K], type[SingleObjectMixin]]:
    """Fixture for a view with the `SingleObjectMixin`."""

    def _view(**kwargs: K) -> type[SingleObjectMixin]:
        """Return a mixin view with the `SingleObjectMixin`."""
        return type(
            "SingleObjectView",
            (mixin_view(), SingleObjectMixin),
            {"model": Article},
            **kwargs,
        )

    return _view


@pytest.fixture(name="multiple_object_view")
def multiple_object_view_factory(mixin_view: Callable) -> Callable:
    """Fixture for a view with the `MultipleObjectMixin`."""

    def _view(**kwargs: K) -> MultipleObjectMixin[Any]:
        """Return a mixin view with the `MultipleObjectMixin`."""
        return type(
            "MultipleObjectView",
            (mixin_view(), MultipleObjectMixin),
            {"model": Article},
            **kwargs,
        )

    return _view


@pytest.fixture(name="form_view")
def form_view_factory(mixin_view: Callable) -> Callable:
    """Fixture for a view with the `FormMixin`."""

    def _view(**kwargs: K) -> BaseFormView[Any]:
        """Return a view with the `FormMixin` mixin."""
        return type(
            "FormView",
            (mixin_view(), BaseFormView),
            {
                "fields": "__all__",
                "http_method_names": ["get", "post"],
            },
            **kwargs,
        )

    return _view


@pytest.fixture(name="model_form_view")
def model_form_view_factory(mixin_view: Callable) -> Callable:
    """Fixture for a view with the `ModelFormMixin`."""

    def _view(**kwargs: K) -> ModelFormMixin[Any, Any]:
        """Return a view with the `ModelFormMixin` mixin."""
        return type(
            "FormView",
            (mixin_view(), ModelFormMixin),
            {
                "fields": "__all__",
                "http_method_names": ["get", "post"],
                "model": Article,
                "object": None,
                "post": lambda s, r, *a, **k: HttpResponse("post"),
            },
            **kwargs,
        )

    return _view


@pytest.fixture(name="form_class")
def form_class_factory() -> Callable:
    """Generate a new form class with given kwargs."""

    def _form(**kwargs: K) -> type[Form]:
        """Return a new form class."""

        class MixinForm(Form):
            class Meta:
                fields = "__all__"

        for k, v in kwargs.items():
            setattr(MixinForm, k, v)
        return MixinForm

    return _form


T_MF = TypeVar("T_MF", bound=ModelForm)


@pytest.fixture(name="model_form_class")
def model_form_class_factory() -> Callable[[K], T_MF]:
    """Generate a new model form class with given kwargs."""

    def _form(**kwargs: K) -> T_MF:
        """Return a new model form class."""

        class MixinModelForm(ModelForm):
            class Meta:
                fields: ClassVar = [k for k in kwargs]
                model = Article

        for k, v in kwargs.items():
            setattr(MixinModelForm, k, v)
        return MixinModelForm

    return _form
