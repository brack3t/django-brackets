---
hide:
- navigation
---
# Form-related Mixins

The mixins in this module should be applied to a Django `Form`, not a view.

## UserFormMixin

When the form is initialized, the "user" keyword argument will be popped
off into the `self.user` name.

```py
from brackets.mixins import UserFormMixin

class ProfileForm(UserFormMixin, ModelForm): ...
```
