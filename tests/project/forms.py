from typing import Any, ClassVar

from django import forms

from brackets import mixins

from .models import Article


class FormWithUserKwarg(mixins.UserFormMixin, forms.Form):
    """Form with a user kwarg."""

    field1 = forms.CharField()


class ArticleForm(forms.ModelForm[Any]):
    """Form for an Article."""

    class Meta:  # noqa: D106
        model = Article
        fields: ClassVar[list[str]] = ["author", "title", "body", "slug"]
