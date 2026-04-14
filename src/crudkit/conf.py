from django.conf import settings

DEFAULTS = {
    "CRUDKIT_PAGINATE_BY": 25,
    "CRUDKIT_PAGE_SIZE_OPTIONS": [10, 25, 50, 100],
    "CRUDKIT_AUDIT_PAGE_SIZE": 25,
}


def get_setting(name: str):
    return getattr(settings, name, DEFAULTS[name])
