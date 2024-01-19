---
hide:
    - navigation
    - toc
---

# django-brackets
## Mixins to make Django's Class-based Views Simpler and Neater

`django-brackets` is a library of mixins to make using class-based views easier. Yes, it's a lot like [`django-braces`](https://github.com/brack3t/django-braces); it should be, we wrote them both. In fact, most of `django-brackets` comes from a rewrite of `django-braces` that was just too big and breaking.

Use these mixins as inspiration for your own, as well! The `PassesTestMixin` is used, for example, to build all of the Access mixins. You can use it to make your own mixins that require a request to pass some arbitrary test!

As you'll see in our [contribution guide], we also love contributions. Send your mixins in today!

## Installation and usage

You'll need to install `django-brackets` via `pip`: `pip install django-brackets`. You do _not_ need to add `brackets` to your `INSTALLED_APPS` in order to use the mixins. In a `views.py` where you need a mixin, you'll import them like: `from brackets import mixins`.

Mixins should be first in your inheritance tree, view classes last. For example:

```py
from django.views import generic
from brackets import mixins

class UserList(mixins.LoginRequiredMixin, generic.ListView):
    ...
```

# Mixins

## HTTP- and request-related mixins

These mixins are all related to authorizing and manipulating requests and responses.

- [Access](mixins/access.md)
- [HTTP](mixins/http.md)
- [Redirects](mixins/redirects.md)

## Databases, forms, and serializers

If your view queries the database, uses forms, or is a form and not a view at all, these mixins may come in handy.

- [Queries](mixins/queries.md)
- [Forms](mixins/forms.md)
- [Form Views](mixins/form_views.md)

## APIs

Mixins related to Django REST Framework and others that don't have a better home.

- [Django REST Framework](mixins/rest_framework.md)
- [Miscellaneous](mixins/misc.md)


[contribution guide]: contribution_guide.md
