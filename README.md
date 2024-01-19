# django-brackets

[Official Documentation](https://django-brackets.readthedocs.io)

`django-brackets` is a small collection of mixins for your class-based
views' needs. Heavily based on [`django-braces`], `brackets` aims to be
a simpler API and lighter tool set than `braces` was.

`django-brackets` is developed against and for still-supported versions
of Django and the latest (or near enough) version of Python. It also
offers mixins for `django-rest-framework` which should work with the
latest release of that package.

As always, [contributions](docs/contributors.md) are welcome.

## Available mixins
(in alphabetical order)

### Django class-based views

* `AllVerbsMixin` - View answers any HTTP verb with a single method.
* `AnonymousRequiredMixin` - Authenticated users are rejected.
* `CacheControlMixin` - Control how the view is cached
* `CSRFExemptMixin` - View does not require CSRF tokens.
* `FormWithUserMixin` - Automatically provides the requesting user to the form.
* `GroupRequiredMixin` - Requesting user must be part of a group.
* `HeaderMixin` - Statically set headers for a view.
* `LoginRequiredMixin` - Non-authenticated users are rejected.
* `MultipleFormsMixin` - View handles multiple forms at once. Taken from [`django-shapeshifter`]
* `NeverCacheMixin` - Mark a view as being uncached.
* `OrderableListMixin` - Allow queryset ordering via query string arguments.
* `PassesTestMixin` - Requests must pass a test before they are dispatched.
* `PassOrRedirectMixin` - Failing requests are redirected to another view.
* `PermissionRequiredMixin` - Requesting user must have specific permissions.
* `PrefetchRelatedMixin` - Add `prefetch_related` clauses into the view's queryset.
* `RecentLoginRequiredMixin` - Users must have logged in recently.
* `RedirectMixin` - Easily redirect requests.
* `RedirectToLoginMixin` - Redirect requests to a login page.
* `SelectRelatedMixin` - Add `select_related` clauses into the view's queryset.
* `SSLRequiredMixin` - Requests must be secure or redirected.
* `StaffUserRequiredMixin` - Requesting user must be a staff member.
* `StaticContextMixin` - Provide a static context to a view.
* `SuperuserRequiredMixin` - Requesting user must be a superuser.

### Django REST Framework

* `MultipleSerializersMixin` - View/Viewset can have multiple serializers.

### Django forms

* `UserFormMixin` - Expects a `"user"` keyword argument, which will become `self.user`.

[`django-braces`]: https://github.com/brack3t/django-braces
[`django-shapeshifter`]: https://github.com/kennethlove/django-shapeshifter
