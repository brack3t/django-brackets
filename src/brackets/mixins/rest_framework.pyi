from typing import Any

from rest_framework.serializers import Serializer

class MultipleSerializersMixin:
    serializer_classes: dict[str, Serializer[Any]]
    def get_serializer_classes(self) -> dict[str, Serializer[Any]]: ...
    def get_serializer_class(self) -> Serializer[Any]: ...