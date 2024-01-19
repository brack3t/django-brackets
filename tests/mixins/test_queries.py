"""Tests for the ORM and QuerySet mixins."""

import pytest
from django.core.exceptions import ImproperlyConfigured

from tests.project.models import Article


@pytest.mark.mixin("SelectRelatedMixin")
class TestSelectRelated:
    """Tests related to the `SelectRelatedMixin`."""

    def test_select_related(self, single_object_view):
        """Test that `select_related` is returned."""
        view = single_object_view()(select_related=["foo", "bar"])
        assert view.get_select_related() == ["foo", "bar"]

    @pytest.mark.parametrize("selected", [None, ""])
    def test_select_related_empty(self, selected, single_object_view):
        """An empty `select_related` should raise an exception."""
        view = single_object_view()(select_related=selected)

        with pytest.raises(ImproperlyConfigured):
            view.get_select_related()

    def test_select_related_non_list(self, single_object_view):
        """A non-list `select_related` should transform to a list."""
        view = single_object_view()(select_related="foo")
        assert view.get_select_related() == ["foo"]

    @pytest.mark.django_db()
    def test_select_related_existing_select_related(self, single_object_view):
        """New select_related should not cancel existing select_related."""
        view = single_object_view()(
            select_related="author",
            queryset=Article.objects.select_related("coauthor"),
            model=None,
        )
        assert view.get_queryset().query.select_related == {
            "author": {},
            "coauthor": {},
        }

    def test_select_related_exception(self, single_object_view):
        """An exception is raised if `select_related` is missing."""
        view = single_object_view()()
        with pytest.raises(ImproperlyConfigured):
            view.get_select_related()


@pytest.mark.mixin("PrefetchRelatedMixin")
class TestPrefetchRelated:
    """Tests related to the `PrefetchRelatedMixin`."""

    def test_prefetch_related(self, single_object_view):
        """Test that `prefetch_related` is returned."""
        view = single_object_view()(prefetch_related=["foo", "bar"])
        assert view.get_prefetch_related() == ["foo", "bar"]

    def test_prefetch_related_string(self, single_object_view):
        """A string `prefetch_related` should transform to a list."""
        view = single_object_view()(prefetch_related="foo")
        assert view.get_prefetch_related() == ["foo"]

    @pytest.mark.parametrize("prefetched", [None, ""])
    def test_prefetch_related_empty(self, prefetched, single_object_view):
        """An empty `prefect_related` should raise an exception."""
        view = single_object_view()(prefetch_related=prefetched)
        with pytest.raises(ImproperlyConfigured):
            view.get_prefetch_related()

    @pytest.mark.django_db()
    def test_prefetch_related_keeps_existing_prefetch_related(self, single_object_view):
        """New prefetch_related should not cancel existing prefetch_related."""
        view = single_object_view()(
            prefetch_related="author",
            queryset=Article.objects.prefetch_related("coauthor"),
        )
        assert view.get_queryset()._prefetch_related_lookups == (
            "coauthor",
            "author",
        )


@pytest.mark.mixin("OrderableListMixin")
class TestOrderableList:
    """Tests related to the `OrderableListMixin`."""

    def test_request_ordering(self, multiple_object_view, rf):
        """Querystring arguments should override the mixin's attributes."""
        request = rf.get("/?order_by=foo&order_dir=desc")
        view = multiple_object_view()(request=request)
        assert view.get_order_from_request() == ("foo", "desc")

    def test_queryset_ordering(self, multiple_object_view, rf):
        """No querystring arguments should use the defaults."""
        request = rf.get("/")
        view = multiple_object_view()(
            orderable_field_default="author",
            orderable_fields=["author"],
            request=request,
        )
        assert view.get_queryset().query.order_by == ("author",)

    def test_queryset_ordering_with_string(self, multiple_object_view, rf):
        """No querystring arguments should use the defaults."""
        request = rf.get("/")
        view = multiple_object_view()(
            orderable_field_default="author",
            orderable_fields="author",
            request=request,
        )
        assert view.get_queryset().query.order_by == ("author",)

    def test_queryset_ordering_with_request(self, multiple_object_view, rf):
        """Querystring arguments should override the queryset's ordering."""
        request = rf.get("/?order_dir=desc")
        view = multiple_object_view()(
            orderable_field_default="author",
            orderable_fields=["author"],
            request=request,
        )
        assert view.get_queryset().query.order_by == ("-author",)

    @pytest.mark.parametrize(
        "method",
        [
            "get_orderable_fields",
            "get_orderable_field_default",
            "get_orderable_direction_default",
        ],
    )
    def test_orderable_fields_exceptions(self, method, multiple_object_view):
        """An exception is raised if `orderable_fields` is missing."""
        view = multiple_object_view()(orderable_direction_default="down")
        with pytest.raises(ImproperlyConfigured):
            getattr(view, method)()

    @pytest.mark.django_db()
    def test_basic_queryset_returned(self, user, multiple_object_view, rf):
        """Test that the correct queryset is returned."""
        request = rf.get("/?order_by=publish_date&order_dir=desc")
        Article.objects.create(title="Ayy", author=user(username="One"))
        Article.objects.create(title="Bee", author=user(username="Two"))
        view = multiple_object_view()(
            orderable_fields=["author"],
            orderable_fields_default="author",
            orderable_direction_default="asc",
            request=request,
        )
        vq = view.get_queryset().values_list(flat=True)
        dq = Article.objects.order_by("-author").values_list(flat=True)
        # Since QuerySets are lazy, we need to force them to evaluate.
        assert list(vq) != list(dq)
