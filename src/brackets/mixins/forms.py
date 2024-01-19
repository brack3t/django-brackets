"""Mixins relating to forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from typing import Any

    from django.db.models import Model

__all__ = [
    "UserFormMixin",
]


class UserFormMixin:
    """Automatically pop request.user from the form's kwargs."""

    def __init__(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Add the user to the form's kwargs."""
        if not issubclass(self.__class__, forms.Form):
            _err_msg = "`UserFormMixin` can only be used with forms or modelforms."
            raise TypeError(_err_msg)

        if "user" in kwargs:
            self.user: Model = kwargs.pop("user")
        super().__init__(*args, **kwargs)
