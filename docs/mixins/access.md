---
hide:
- navigation
---

# Access mixins

A lot of time is spent handling authentication and authorization in Django
projects, from setting up your methods to special rules for special views.
These mixins are aimed at making it easier to control access to your view.

## PassesTestMixin

The `PassesTestMixin` is the base for most of the mixins in this module.
It requires you to provide a method and that method's name. The view will
run that method before anything happens in `dispatch`. If the test method
returns `False` or an equivalent, the view's `dispatch` method will be
skipped and the `handle_test_failure` method will be called. Override
`handle_test_failure` to control what happens when the request doesn't
pass your test.

```python
from brackets.mixins import PassesTestMixin


class IndexView(PassesTestMixin, TemplateView):
    dispatch_test = "is_unchained"

    def is_unchained(self):
        return not self.request.is_chained
```

The above view would require a request to have `is_chained` defined and
falsey in order to pass and the view be executed. By overriding
`get_test_method`, you can control how the dispatch test is discovered.
Overriding `handle_test_failure` will let you customize what happens after
a failed test.

Using this mixin, you can create all of the other mixins in this module.
That's what we did.

## PassOrRedirectMixin

The `PassOrRedirectMixin` combines two powerful mixins: `PassesTestMixin`
and the [`RedirectMixin`] from [the redirect mixins].

If the view's test doesn't pass, by default the request will be redirected
to whatever URL you provide in the `redirect_url` attribute. If you'd like
to control how the redirection is accomplished, override `redirect`. If
you'd like to customize how the redirect URL is discovered, you'll want
to override `get_redirect_url`.

```py
from brackets.mixins import PassOrRedirectMixin

class InOrOutView(PassOrRedirectMixin, View):
    redirect_url = "/login/"
    redirect_unauthenticated_users = True
```

The `redirect_unauthenticated_users` attribute directs the mixin to either
use the `redirect` method or to use whatever failure handler is next in
the chain.

## SuperuserRequiredMixin

The `SuperuserRequiredMixin` is a fairly unsurprising mixin. If the user
requesting the view is not authenticated and a superuser, they're redirected
elsewhere. You'll want to override the default `test_superuser` if you
have a special way of determining user levels.

```py
from brackets.mixins import SuperuserRequiredMixin

class PhoneBooth(SuperuserRequiredMixin, DetailView): ...
```

## StaffUserRequiredMixin

Much like `SuperuserRequiredMixin`, the `StaffUserRequiredMixin` requires
the view to be requested by a user where `is_staff` is `True`. If you need
to customize this discovery, override `test_staffuser`.

```py
from brackets.mixins import StaffUserRequiredMixin

class WizardInventory(StaffUserRequiredMixin, DetailView): ...
```

## GroupRequiredMixin

The `GroupRequiredMixin` is a little different from `SuperuserRequired`
and `StaffUserRequired`. It will take a single group name or a list of
group names, and then ensure that the requesting user is in at least one
of them.

```py
from brackets.mixins import GroupRequiredMixin

class PrivateGroupView(GroupRequiredMixin, ListView):
    group_required = "private_group"
```

Overriding `check_membership` will let you customize this membership
requirement.

## AnonymousRequiredMixin

One of the simplest mixins, the `AnonymousRequiredMixin` redirects any
requests coming from an authenticated user. This mixin is useful on views
related to login or account creation, since there's little to no reason
for an authenticated user to be on those pages.

```py
from brackets.mixins import AnonymousUserMixin

class NewSubscriberBenefits(AnonymousUserRequiredMixin, DetailView): ...
```

## LoginRequiredMixin

Much like the `AnonymousRequiredMixin`, the `LoginRequiredMixin` redirects
any requests that aren't from an authenticated user.

```py
from brackets.mixins import LoginRequiredMixin

class MembersOnly(LoginRequiredMixin, DetailView): ...
```

## RecentLoginRequiredMixin

The `RecentLoginRequiredMixin` is exactly the same as the `LoginRequiredMixin`
except that it checks the age of the user's authentication. Overriding
`max_age` with a new value, in seconds, will allow you to control how
long they can go between authentications.

```py
from brackets.mixins import RecentLoginRequiredMixin

class MembersOnly(RecentLoginRequiredMixin, DetailView):
    max_age: 3600  # They must login within the last hour
```

## PermissionRequiredMixin

The `PermissionRequiredMixin` is probably the most complex of the
access-related mixins. Permissions are a very customizable system in Django.
In this mixin, too, you're allowed to have optional and required permissions.

The `permission_required` attribute is where most of the work is done.
It's expected to be a dictionary with two keys: `"all"` and `"any"`. The
`"all"` key indicates permissions which the user _must_ have, and they
must have _all_ of them. The `"any"` list of permissions, though, will
allow a user through if they have any of the listed permissions.

```py
from brackets.mixins import PermissionRequiredMixin

class EditAccountView(PermissionRequiredMixin, UpdateView):
    permission_required = {
        "all": ["account.can_edit"],
        "any": ["account.can_manage", "account.can_administer"]
    }
```

The above view would require a user to have the `account.can_edit` permission.
The user wouldn't have to have both the `account.can_manage` or
`account.can_administer` permissions. In fact, they don't have to have
either! `"any"` also allows for "none".

## SSLRequiredMixin

The `SSLRequiredMixin` only allows through requests that come from a secure
connection. By default, requests are redirected to their `https` equivalent.
You can control this by setting `redirect_to_ssl` to `False`; the view
will now return a `BadRequest` instead of redirecting.

```py
from brackets.mixins import RecentLoginRequiredMixin

class WeTakeSecuritySeriously(SSLRequiredMixin, TemplateView):
    redirect_to_ssl = False
```

If you need to customize the redirection, override `handle_test_failure`.

[`RedirectMixin`]: redirects.md#RedirectMixin
[the redirect mixins]: redirects.md
