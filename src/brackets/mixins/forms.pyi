from typing import Any, Type

from django.db import models

class UserFormMixin:
    user: Type[models.Model]
    def __init__(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None: ...
