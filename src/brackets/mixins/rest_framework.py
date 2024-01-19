"""Mixins related to Django REST Framework."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from brackets.exceptions import BracketsConfigurationError

if TYPE_CHECKING:  # pragma: no cover
    from typing import ClassVar, Optional

    from rest_framework.serializers import Serializer

__all__ = ["MultipleSerializersMixin"]


class MultipleSerializersMixin:
    """Mixin to use multiple serializers for a view.

    This mixin is useful if you want to use different serializers for
    different HTTP methods. For example, you may want to return a
    different set of fields for a GET request than for a POST request.
    """

    serializer_classes: ClassVar[Optional[dict[str, type[Serializer[Any]]]]] = None

    def get_serializer_classes(self) -> dict[str, type[Serializer[Any]]]:
        """Get necessary serializer classes."""
        if not self.serializer_classes:
            raise BracketsConfigurationError(
                "'%s' should either include a `serializer_classes` attribute, "
                "or override the `get_serializer_classes()` method."
                % self.__class__.__name__
            )

        return self.serializer_classes

    def get_serializer_class(self) -> type[Serializer[Any]]:
        """Get the serializer class to use for this request.

        Defaults to using `super().serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (E.g. admins get full serialization, others get basic serialization)
        """
        serializer_classes = self.get_serializer_classes()
        if not serializer_classes:
            return super().get_serializer_class()
        return serializer_classes[self.request.method.lower()]
