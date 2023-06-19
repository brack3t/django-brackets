---
hide:
- navigation
---

# Miscellaneous mixins

Sometimes mixins just don't have a good home.

## StaticContextMixin

This mixin allows you to set static values which will always be injected
into the view's `context` that's used to render templates.

```py
from brackets.mixins import StaticContextMixin

class WelcomePage(StaticContextMixin, TemplateView):
    static_context = {"greeting": "Go away"}
```

If you'd like to provide your static context in a dynamic way...you can
so by overriding the `get_static_context` method.
