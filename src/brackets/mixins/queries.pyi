from collections.abc import Iterable

from django.db.models import Model, QuerySet
from django.http import HttpRequest

from . import A, CanQuery, HasRequest, K

class SelectRelatedMixin(CanQuery):
    queryset: QuerySet[Model]
    select_related: str | list[str] | tuple[str]
    def get_select_related(self) -> list[str]: ...
    def get_queryset(self) -> QuerySet[Model]: ...

class PrefetchRelatedMixin(CanQuery):
    prefetch_related: K
    queryset: QuerySet[Model]
    def get_prefetch_related(self) -> list[str]: ...
    def get_queryset(self) -> QuerySet[Model]: ...

class OrderableListMixin(CanQuery, HasRequest):
    request: HttpRequest
    orderable_fields: list[str]
    orderable_field_default: str
    orderable_direction_default: str
    queryset: QuerySet[Model]
    def __init__(self, *args: A, **kwargs: K) -> None: ...
    def get_orderable_fields(self) -> Iterable[str]: ...
    def get_orderable_field_default(self) -> str: ...
    def get_orderable_direction_default(self) -> str: ...
    def get_order_from_request(self) -> Iterable[str]: ...
    def get_queryset(self) -> QuerySet[Model]: ...
