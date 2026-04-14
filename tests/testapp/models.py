from django.db import models
from django.urls import reverse


class Widget(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("widget-update", kwargs={"pk": self.pk})


class Gadget(models.Model):
    """A related model to test delete protection."""

    widget = models.ForeignKey(Widget, on_delete=models.PROTECT, related_name="gadgets")
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name
