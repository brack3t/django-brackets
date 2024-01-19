---
hide:
- navigation
---

# Django REST Framework mixins

Increasingly, if you use Django, you probably use Django REST Framework
with it. These mixins will make working with DRF simpler.

## MultipleSerializerMixin

This mixin, like the [form_views.MultipleFormView] allows you to specify,
validate, and handle multiple serializers in a single view. Unlike that
mixin, however, the serializers are assumed to be different based on the
HTTP verb their view was requested by. You can override this by changing
`get_serializer_class`

```py
from brackets.mixins import MultipleSerializersMixin

class SerialCereal(MultipleSerializersMixin, ViewSet):
    serializer_classes = {
        "get": FullSerializer,
        "post": FullSerializerWithValidation
    }
```

[form_views.MultipleFormView]: form_views.md#multipleformsmixin
