from __future__ import annotations

from django.db import models

from typing import Type

from . import A, K


class UserFormMixin:
    user: Type[models.Model]
    def __init__(self, *args: A, **kwargs: K) -> None: ...
