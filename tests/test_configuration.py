import pytest

from crudkit.conf import get_setting


class TestConfiguration:
    def test_default_paginate_by(self):
        assert get_setting("CRUDKIT_PAGINATE_BY") == 25

    def test_default_page_size_options(self):
        assert get_setting("CRUDKIT_PAGE_SIZE_OPTIONS") == [10, 25, 50, 100]

    def test_default_audit_page_size(self):
        assert get_setting("CRUDKIT_AUDIT_PAGE_SIZE") == 25

    def test_override_paginate_by(self, settings):
        settings.CRUDKIT_PAGINATE_BY = 50
        assert get_setting("CRUDKIT_PAGINATE_BY") == 50

    def test_override_page_size_options(self, settings):
        settings.CRUDKIT_PAGE_SIZE_OPTIONS = [5, 10]
        assert get_setting("CRUDKIT_PAGE_SIZE_OPTIONS") == [5, 10]

    def test_override_audit_page_size(self, settings):
        settings.CRUDKIT_AUDIT_PAGE_SIZE = 10
        assert get_setting("CRUDKIT_AUDIT_PAGE_SIZE") == 10
