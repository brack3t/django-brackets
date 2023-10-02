"""Mixins that don't have a better home."""
from __future__ import annotations

from typing import Any, ClassVar

from brackets.exceptions import BracketsConfigurationError

__all__ = ["StaticContextMixin"]


class StaticContextMixin:
    """A mixin for adding static items to the context."""

    static_context: ClassVar[dict[str, Any]] = {}

    def get_static_context(self) -> dict[str, Any]:
        """Get the static context to add to the view's context."""
        _class = self.__class__.__name__
        if not self.static_context:
            _err_msg = (
                f"{_class} is missing the static_context attribute. "
                f"Define `{_class}.static_context`, or override "
                f"`{_class}.get_static_context()`."
            )
            raise BracketsConfigurationError(_err_msg)

        return self.static_context

    def get_context_data(self) -> dict[str, Any]:
        """Add the static context to the view's context."""
        context: dict[str, Any] = super().get_context_data()
        context.update(self.get_static_context())
        return context
