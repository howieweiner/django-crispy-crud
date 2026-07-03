class AuditOnUpdateOnly:
    """Mixin to only audit updates, not creation."""

    def save(self, *args, **kwargs):
        try:
            from auditlog.context import disable_auditlog
        except ImportError as e:
            raise ImportError(
                "django-auditlog is required for AuditOnUpdateOnly. Install it with: pip install django-crispy-crud[audit]"
            ) from e

        is_new = self.pk is None
        if is_new:
            with disable_auditlog():
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
