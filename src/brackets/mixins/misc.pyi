from . import HasContext, K

class StaticContextMixin(HasContext):
    context: K
    static_context: K
    def get_static_context(self) -> K: ...
    def get_context_data(self) -> K: ...
