from typing import Any

from django.core.serializers.json import DjangoJSONEncoder


class SetJSONEncoder(DjangoJSONEncoder):
    """A custom JSON Encoder for `set`."""

    def default(self, obj: Any) -> Any:  # noqa ANN001
        """Control default methods of encoding data."""
        if isinstance(obj, set):
            return list(obj)
        return super(DjangoJSONEncoder, self).default(obj)
