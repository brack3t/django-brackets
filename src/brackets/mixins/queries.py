"""Mixins related to Django ORM queries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from brackets.exceptions import BracketsConfigurationError

if TYPE_CHECKING:  # pragma: no cover
    from typing import Sequence

    from django.db.models import Model, QuerySet

__all__ = ["SelectRelatedMixin", "PrefetchRelatedMixin", "OrderableListMixin"]


class SelectRelatedMixin:
    """A mixin for adding select_related to the queryset."""

    select_related: str | Sequence[str] = ""

    def get_select_related(self) -> Sequence[str]:
        """Get the fields to be select_related."""
        _class = self.__class__.__name__

        if not self.select_related:
            _err_msg = (
                f"{_class} is missing the select_related attribute. "
                f"Define `{_class}.select_related`, or override "
                f"`{_class}.get_select_related()`."
            )
            raise BracketsConfigurationError(_err_msg)

        if isinstance(self.select_related, str):
            self.select_related = [self.select_related]

        return self.select_related

    def get_queryset(self) -> QuerySet[Model]:
        """Add select_related to the queryset."""
        queryset: QuerySet[Model] = super().get_queryset()
        select_related = self.get_select_related()
        return queryset.select_related(*select_related)


class PrefetchRelatedMixin:
    """A mixin for adding prefetch_related to the queryset."""

    prefetch_related: str | Sequence[str] = ""

    def get_prefetch_related(self) -> Sequence[str]:
        """Get the fields to be prefetch_related."""
        _class = self.__class__.__name__
        if not self.prefetch_related:
            _err_msg = (
                f"{_class} is missing the prefetch_related attribute. "
                f"Define `{_class}.prefetch_related`, or override "
                f"`{_class}.get_prefetch_related()`."
            )
            raise BracketsConfigurationError(_err_msg)

        if isinstance(self.prefetch_related, str):
            self.prefetch_related = [self.prefetch_related]

        return self.prefetch_related

    def get_queryset(self) -> QuerySet[Model]:
        """Add prefetch_related to the queryset."""
        queryset: QuerySet[Model] = super().get_queryset()
        prefetch_related = self.get_prefetch_related()
        return queryset.prefetch_related(*prefetch_related)


class OrderableListMixin:
    """A mixin for adding query-string based ordering to the queryset."""

    orderable_fields: str | Sequence[str] = ""
    orderable_field_default = ""
    orderable_direction_default: str = "asc"  # "asc" or "desc"

    def get_orderable_fields(self) -> Sequence[str]:
        """Get fields to use for ordering."""
        if not self.orderable_fields:
            _class = self.__class__.__name__
            _err_msg = (
                f"{_class} is missing the orderable_fields attribute. "
                f"Define `{_class}.orderable_fields`, or override "
                f"`{_class}.get_orderable_fields()`."
            )
            raise BracketsConfigurationError(_err_msg)
        if isinstance(self.orderable_fields, str):
            self.orderable_fields = [self.orderable_fields]
        return self.orderable_fields

    def get_orderable_field_default(self) -> str:
        """Get the default ordering field."""
        if not self.orderable_field_default:
            _class = self.__class__.__name__
            _err_msg = (
                f"{_class} is missing the orderable_field_default attribute. "
                f"Define `{_class}.orderable_field_default`, or override "
                f"`{_class}.get_orderable_field_default()`."
            )
            raise BracketsConfigurationError(_err_msg)
        return self.orderable_field_default

    def get_orderable_direction_default(self) -> str:
        """Get the default ordering direction."""
        direction = self.orderable_direction_default
        if not direction or direction not in ["asc", "desc"]:
            _class = self.__class__.__name__
            _err_msg = f"{_class}.orderable_direction_default must be 'asc' or 'desc'."
            raise BracketsConfigurationError(_err_msg)
        return direction

    def get_order_from_request(self) -> Sequence[str]:
        """Use the query string to determine the ordering."""
        field: str = self.request.GET.get("order_by", "").lower()
        direction: str = self.request.GET.get("order_dir", "").lower()

        if not field:
            field: str = self.get_orderable_field_default()
        if not direction:
            direction: str = self.get_orderable_direction_default()
        return field, direction

    def get_queryset(self) -> QuerySet[Model]:
        """Order the queryset."""
        queryset: QuerySet[Model] = super().get_queryset()

        field, direction = self.get_order_from_request()
        allowed_fields: Sequence[str] = self.get_orderable_fields()

        direction: str = "-" if direction == "desc" else ""

        if field in allowed_fields:
            return queryset.order_by(f"{direction}{field}")

        return queryset
