from typing import Any, Optional

from django.http import HttpRequest
from rest_framework.serializers import Serializer

class MultipleSerializersMixin:
    request: HttpRequest
    serializer_classes: Optional[dict[str, type[Serializer[Any]]]]
    def get_serializer_classes(self) -> dict[str, Serializer[Any]]: ...
    def get_serializer_class(self) -> type[Serializer[Any]]: ...
