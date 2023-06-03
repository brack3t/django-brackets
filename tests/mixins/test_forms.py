"""Tests relating to the form mixins."""
import pytest
from django import forms

from brackets import mixins


class TestUserFormMixin:
    """Tests for the UserFormMixin."""

    class InvalidForm(mixins.UserFormMixin):
        """A non-form form."""

    class DoesNothing:
        """A non-form."""

    class ValidForm(mixins.UserFormMixin, forms.Form):
        """A form form."""

    def test_invalid_class(self):
        """Invalid forms raise an exception."""
        with pytest.raises(TypeError):
            self.InvalidForm()

    @pytest.mark.parametrize(("form_class", "user"), [(ValidForm, True), (ValidForm, False)])
    def test_form_has_user(self, form_class, user, admin_user):
        """Valid forms contain the user."""
        form_kwargs = {"user": admin_user} if user else {}
        form = form_class(**form_kwargs)
        try:
            assert form.user == admin_user
        except AttributeError:
            assert not user
        else:
            assert user
