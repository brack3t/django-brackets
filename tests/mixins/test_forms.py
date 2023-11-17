"""Tests relating to the form mixins."""
import pytest
from django import forms

from brackets import mixins


class ValidForm(mixins.UserFormMixin, forms.Form):
    """Valid forms extend both classes."""


class TestUserFormMixin:
    """Tests for the UserFormMixin."""

    def test_invalid_class(self):
        """Invalid forms raise an exception."""

        class _Form(mixins.UserFormMixin):
            """Testing purposes only"""

        with pytest.raises(TypeError):
            _Form()

    @pytest.mark.parametrize(
        ("form_class", "user"), [(ValidForm, True), (ValidForm, False)]
    )
    def test_form_has_user(self, form_class, user, admin_user):
        """Valid forms contain the user."""
        form_kwargs = {"user": admin_user} if user else {}
        form = form_class(**form_kwargs)
        try:
            assert form.user == admin_user
        except AttributeError:
            # The form does not have a user
            assert not user
        else:
            # The form has a user
            assert user
