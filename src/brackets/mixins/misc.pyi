from typing import Any, ClassVar

from . import HasContext

class StaticContextMixin(HasContext):
    context: ClassVar[dict[str, Any]]
    static_context: dict[str, Any]
    def get_static_context(self) -> dict[str, Any]: ...
    def get_context_data(self, **kwargs: dict[Any, Any]) -> dict[str, Any]: ...
