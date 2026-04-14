import django
from django.apps import apps


class TestPackageInstallation:
    def test_crudkit_app_is_installed(self):
        assert apps.is_installed("crudkit")

    def test_app_config_loads(self):
        app_config = apps.get_app_config("crudkit")
        assert app_config.name == "crudkit"
        assert app_config.verbose_name == "CRUD Kit"

    def test_app_config_class(self):
        from crudkit.apps import CrudKitConfig

        assert CrudKitConfig.name == "crudkit"
        assert CrudKitConfig.default_auto_field == "django.db.models.BigAutoField"

    def test_package_importable(self):
        import crudkit

        assert crudkit is not None

    def test_conf_defaults(self):
        from crudkit.conf import get_setting

        assert get_setting("CRUDKIT_PAGINATE_BY") == 25
        assert get_setting("CRUDKIT_PAGE_SIZE_OPTIONS") == [10, 25, 50, 100]
        assert get_setting("CRUDKIT_AUDIT_PAGE_SIZE") == 25

    def test_conf_override(self, settings):
        from crudkit.conf import get_setting

        settings.CRUDKIT_PAGINATE_BY = 50
        assert get_setting("CRUDKIT_PAGINATE_BY") == 50

    def test_testapp_is_installed(self):
        assert apps.is_installed("tests.testapp")

    def test_submodules_importable(self):
        from crudkit import views, forms, models, utils
        from crudkit.views import mixins as view_mixins
        from crudkit.views import utils as view_utils
        from crudkit.forms import crispy
        from crudkit.models import mixins as model_mixins
        from crudkit.utils import url_utils

        assert view_mixins is not None
        assert view_utils is not None
        assert crispy is not None
        assert model_mixins is not None
        assert url_utils is not None
