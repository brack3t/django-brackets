---
hide:
- navigation
---

# Form-related View Mixins

Many class-based views rely on forms to power them. Whether you're creating
a new instance, editing an existing one, or accepting customer feedback,
form views are your friend. The mixins in this module relate to these views.

## CSRFExemptMixin

This mixin marks a view as being exempt from CSRF checks. This is often
handy for AJAX-related views.

```py
from brackets.mixins import CSRFExemptMixin

class UnshieldedForm(CSRFExemptMixin, FormView): ...
```

## FormWithUserMixin

The `FormWithUserMixin` provides a keyword argument to your form named
`user`. This keyword argument's value is the `request.user`. Combine
this mixin with the [forms.UserFormMixin] for best results.

```py
from brackets.mixins import FormWithUserMixin

class UserForm(FormWithUserMixin, FormView): ...
```

## MultipleFormsMixin

If you've ever found yourself having to handle multiple Django forms in
the same view, you know it can be a pain. This mixin aims to reduce or
even remove that complexity completely.

Three attributes have been added, with corresponding methods, that will
allow you to configure your view. All are dictionaries where the key is
used to refer to the form.

```py
from brackets.mixins import MultipleFormMixin

class UserAndAccountView(MultipleFormMixin, FormView):
    form_classes = {"user": UserForm, "account": AccountForm}
    form_initial_values = {"account_id": 0}

    def get_form_instances(self):
        instances = super().get_form_instances()
        intances.update({"user": self.request.user})
        return instances
```

- `form_classes` values are the form _classes_ themselves. Use
  `get_form_classes` to provide form classes programmatically.
- `form_initial_values` values are dictionaries of initial data for the
  forms. You can also provide this dictionary via `get_initial`
- `form_instances` values are model instances to be provided to model
  forms. Since this is usually more complicated, expect to override the
  behavior in `get_instance`.

[forms.UserFormMixin]: forms.md#UserFormMixin
