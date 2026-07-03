from django.conf import settings

DEFAULTS = {
    "CRISPY_CRUD_PAGINATE_BY": 25,
    "CRISPY_CRUD_PAGE_SIZE_OPTIONS": [10, 25, 50, 100],
    "CRISPY_CRUD_AUDIT_PAGE_SIZE": 25,
}


def get_setting(name: str):
    return getattr(settings, name, DEFAULTS[name])
