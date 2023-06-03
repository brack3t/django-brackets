"""Tests relating to the form mixins."""
import pytest
from django import forms

from brackets import mixins


class TestUserFormMixin:
    """Tests for the UserFormMixin."""

    class InvalidForm(mixins.UserFormMixin):
        """A non-form form."""

    class ValidForm(mixins.UserFormMixin, forms.Form):
        """A form form."""

    def test_invalid_class(self):
        """Invalid forms raise an exception."""
        with pytest.raises(TypeError):
            self.InvalidForm()

    def test_form_has_user(self, admin_user):
        """Valid forms contain the user."""
        form = self.ValidForm(user=admin_user)
        assert form.user == admin_user
