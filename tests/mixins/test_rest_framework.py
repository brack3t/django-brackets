"""Tests related to the Django REST Framework-related mixins."""
from typing import Any, ClassVar

import pytest
from django.core.exceptions import ImproperlyConfigured
from rest_framework.generics import GenericAPIView
from rest_framework.serializers import Serializer

from brackets.mixins import MultipleSerializersMixin

SC = dict[str, type[Serializer[Any]]]


class TestMultipleSerializers:
    """Tests related to the `MultipleSerializersMixin`."""

    class _TestSerializer(Serializer[Any]):
        """Test serializer."""

    def test_get_serializer_class(self, rf):
        """Views are able to return a specific serializer class."""

        class _View(MultipleSerializersMixin, GenericAPIView):
            serializer_classes: ClassVar[SC] = {
                "get": self._TestSerializer,
                "post": self._TestSerializer,
            }

        request = rf.get("/")
        view = _View()
        view.setup(request)
        assert view.get_serializer_class() == self._TestSerializer

    def test_get_serializer_class_missing(self):
        """Views without `serializer_classes` raise an exception."""

        class _View(MultipleSerializersMixin, GenericAPIView):
            pass

        with pytest.raises(ImproperlyConfigured):
            _View().get_serializer_class()

    def test_get_serializer_class_invalid(self, rf):
        """Views with invalid `serializer_classes` raise an exception."""

        class _View(MultipleSerializersMixin, GenericAPIView):
            serializer_classes = "test"  # type: ignore

        request = rf.get("/")
        view = _View()
        view.setup(request)

        with pytest.raises(TypeError):
            view.get_serializer_class()

    def test_get_serializer_class_invalid_method(self, rf):
        """Views without a serializer for the method raise an exception."""

        class _View(MultipleSerializersMixin, GenericAPIView):
            serializer_classes: ClassVar[SC] = {"post": self._TestSerializer}

        request = rf.get("/")
        view = _View()
        view.setup(request)

        with pytest.raises(KeyError):
            view.get_serializer_class()

    def test_get_original_serializer(self, rf):
        """Views are able to return the original serializer class."""

        class _View(MultipleSerializersMixin, GenericAPIView):
            serializer_class = self._TestSerializer
            serializer_classes: ClassVar[SC] = {
                "get": Serializer,
                "post": Serializer,
            }

            def get_serializer_classes(self):
                return []

        request = rf.get("/")
        view = _View()
        view.setup(request)
        assert view.get_serializer_class() == self._TestSerializer
