"""Article and CanonicalArticle models for the django-brackets project."""
from __future__ import annotations

from django.db import models


class Article(models.Model):
    """A small but useful model for testing most features."""

    author = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.CASCADE
    )
    coauthor = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=30)
    body = models.TextField()
    slug = models.SlugField(blank=True)

    class Meta:  # noqa: D106
        app_label = "project"

    def __str__(self) -> str:
        """Return the string version of an Article."""
        return f"_{self.title}_ by {self.author}."


class CanonicalArticle(models.Model):
    """Model specifically for testing the canonical slug mixins."""

    author = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.CASCADE
    )
    title = models.CharField(max_length=30)
    body = models.TextField()
    slug = models.SlugField(blank=True)

    class Meta:  # noqa: D106
        app_label = "project"

    def __str__(self) -> str:
        """Return the string version of a CanonicalArticle."""
        return f"_{self.title}_ by {self.author}."

    def get_canonical_slug(self) -> str:
        """Return the slug of record."""
        if self.author:
            return f"{self.author.username}-{self.slug}"
        return f"unauthored-{self.slug}"
