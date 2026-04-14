import pytest

from crudkit.models.mixins import AuditOnUpdateOnly


class TestAuditOnUpdateOnly:
    def test_class_exists(self):
        assert AuditOnUpdateOnly is not None

    def test_has_save_method(self):
        assert hasattr(AuditOnUpdateOnly, "save")
