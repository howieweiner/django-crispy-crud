from django.apps import apps


class TestPackageInstallation:
    def test_crispy_crud_app_is_installed(self):
        assert apps.is_installed("crispy_crud")

    def test_app_config_loads(self):
        app_config = apps.get_app_config("crispy_crud")
        assert app_config.name == "crispy_crud"
        assert app_config.verbose_name == "Crispy CRUD"

    def test_app_config_class(self):
        from crispy_crud.apps import CrispyCrudConfig

        assert CrispyCrudConfig.name == "crispy_crud"
        assert CrispyCrudConfig.default_auto_field == "django.db.models.BigAutoField"

    def test_package_importable(self):
        import crispy_crud

        assert crispy_crud is not None

    def test_conf_defaults(self):
        from crispy_crud.conf import get_setting

        assert get_setting("CRISPY_CRUD_PAGINATE_BY") == 25
        assert get_setting("CRISPY_CRUD_PAGE_SIZE_OPTIONS") == [10, 25, 50, 100]
        assert get_setting("CRISPY_CRUD_AUDIT_PAGE_SIZE") == 25

    def test_conf_override(self, settings):
        from crispy_crud.conf import get_setting

        settings.CRISPY_CRUD_PAGINATE_BY = 50
        assert get_setting("CRISPY_CRUD_PAGINATE_BY") == 50

    def test_testapp_is_installed(self):
        assert apps.is_installed("tests.testapp")

    def test_submodules_importable(self):
        from crispy_crud.views import mixins as view_mixins
        from crispy_crud.views import utils as view_utils
        from crispy_crud.forms import crispy
        from crispy_crud.models import mixins as model_mixins
        from crispy_crud.utils import url_utils

        assert view_mixins is not None
        assert view_utils is not None
        assert crispy is not None
        assert model_mixins is not None
        assert url_utils is not None
