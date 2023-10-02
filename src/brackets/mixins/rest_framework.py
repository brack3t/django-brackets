"""Mixins related to Django REST Framework."""

from __future__ import annotations

import typing

from brackets.exceptions import BracketsConfigurationError

if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Type

    from rest_framework.serializers import Serializer

__all__ = ["MultipleSerializersMixin"]


class MultipleSerializersMixin:
    """Mixin to use multiple serializers for a view.

    This mixin is useful if you want to use different serializers for
    different HTTP methods. For example, you may want to return a
    different set of fields for a GET request than for a POST request.
    """

    serializer_classes: dict[str, Type[Serializer]] = {}

    def get_serializer_classes(self) -> dict[str, Type[Serializer]]:
        """Get necessary serializer classes."""
        _class = self.__class__.__name__
        if not self.serializer_classes:
            _err_msg = (
                f"{_class} is missing the serializer_classes attribute. "
                f"Define `{_class}.serializer_classes`, or override "
                f"`{_class}.get_serializer_classes()`."
            )
            raise BracketsConfigurationError(_err_msg)

        if not isinstance(self.serializer_classes, dict):
            _err_msg = f"{_class}.serializer_classes must be a dictionary."
            raise BracketsConfigurationError(_err_msg)

        return self.serializer_classes

    def get_serializer_class(self) -> Type[Serializer]:
        """Get the serializer class to use for this request.

        Defaults to using `super().serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (E.g. admins get full serialization, others get basic serialization)
        """
        serializer_classes = self.get_serializer_classes()
        return serializer_classes[self.request.method.lower()]