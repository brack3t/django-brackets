---
hide:
- navigation
---

# Query Mixins

All of the mixins in here relate to controlling the queries that your views
make. Use these views to reduce the number of queries being ran.

## SelectRelatedMixin

Adds `select_related` clauses to your query.

```py
from brackets.mixins import SelectRelatedMixin

class SuperDetailView(SelectRelatedMixin, DetailView):
    select_related = "profile"
```

You can select multiple fields by providing a list (e.g.
`select_related = ["profile", "pet_set"]`).

## PrefetchRelatedMixin

Much like the `SelectRelatedMixin`, the `PrefetchRelatedMixin` will add
`prefetch_related` clauses into your query.


```py
from brackets.mixins import PrefetchRelatedMixin

class SuperListView(PrefetchRelatedMixin, ListView):
    prefetch_related = ["user", "account"]
```

You can provide a single field as a string.

## OrderableListMixin

The `OrderableListMixin` injects directives to order your queryset via
your URL. An example might be a URL like `example.com/widgets/?order_by=manufacturer&order_dir=desc`, which would order a page full of widgets by their manufacturer
in descending order.

```py
class SortYourselfOut(OrderableListMixin, ListView):
    orderable_fields = ["manufacturer", "make", "model"]
    orderable_field_default = "make"
    orderable_direction_default = "asc"
```
