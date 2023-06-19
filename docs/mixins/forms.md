---
hide:
- navigation
---
# Form-related Mixins

The mixin in this module is meant to be applied to a Django `Form`.

## UserFormMixin

The `UserFormMixin` should be applied to a form, not a view. When the
form is initialized, the "user" keyword argument will be popped off into
the `self.user` name.

```py
from brackets.mixins import UserFormMixin

class ProfileForm(UserFormMixin, ModelForm): ...
```
