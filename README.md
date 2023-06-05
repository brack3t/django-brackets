# django-brackets

`django-brackets` is a small collection of mixins for your class-based
views' needs. Heavily based on [`django-braces`], `brackets` aims to be
a simpler API and lighter tool set than `braces` was.

`django-brackets` is developed against and for still-supported versions
of Django and the latest (or near enough) version of Python. It also
offers mixins for `django-rest-framework` which should work with the
latest release of that package.

As always, contributions are welcome.

## Available mixins:

* `PassesTestMixin` - Requests must pass a test before they are dispatched.
* `PassOrRedirectMixin` - Failing requests are redirected to another view.
* `SuperuserRequiredMixin` - Requesting user must be a superuser.
* `StaffUserRequiredMixin` - Requesting user must be a staff member.
* `GroupRequiredMixin` - Requesting user must be part of a group.
* `AnonymousRequiredMixin` - Authenticated users are rejected.
* `LoginRequiredMixin` - Non-authenticated users are rejected.
* `RecentLoginRequiredMixin` - Users must have logged in recently.
* `PermissionRequiredMixin` - Requesting user must have specific permissions.
* `SSLRequiredMixin` - Requests must be secure or redirected.
* `FormWithUserMixin` - Automatically provides the requesting user to the form.
* `CSRFExemptMixin` - View does not require CSRF tokens.
* `MultipleFormsMixin` - View handles multiple forms at once. Taken from [`django-shapeshifter`]
* `AllVerbsMixin` - View answers any HTTP verb with a single method.
* `HeaderMixin` - Statically set headers for a view.
* `CacheControlMixin` - Control how the view is cached
* `NeverCacheMixin` - Mark a view as being uncached.
* `StaticContextMixin` - Provide a static context to a view.
* `SelectRelatedMixin` - Add `select_related` clauses into the view's queryset.
* `PrefetchRelatedMixin` - Add `prefetch_related` clauses into the view's queryset.
* `OrderableListMixin` - Allow queryset ordering via query string arguments.
* `RedirectMixin` - Easily redirect requests.
* `RedirectToLoginMixin` - Redirect requests to a login page.
* `MultipleSerializersMixin` - View/Viewset can have multiple serializers.
* `UserFormMixin` - Expects a `"user"` keyword argument, which will become `self.user`.



[`django-braces`]: https://github.com/brack3t/django-braces
[`django-shapeshifter`]: https://github.com/kennethlove/django-shapeshifter
