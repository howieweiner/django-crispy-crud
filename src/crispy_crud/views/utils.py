from __future__ import annotations

from urllib.parse import urlencode

from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme


def add_page_context_data(
    context: dict,
    section: str,
    heading: str | None = None,
    model_name: str | None = None,
    delete_action: str | None = None,
    create_action: str | None = None,
    create_action_label: str | None = None,
) -> dict:
    context.update(
        {
            "heading": heading,
            "section": section,
            "model_name": model_name,
            "delete_action": delete_action,
            "create_action": create_action,
            "create_action_label": create_action_label,
        }
    )
    return context


def get_cancel_url(request: HttpRequest | None, url_name: str | None, kwargs: dict | None = None) -> str | None:
    """
    Return the cancel URL, with query params preserved.
    Falls back to the request referrer (when same-site) if url_name is not provided.
    """
    if request is None:
        return None

    if url_name:
        action = str(reverse_lazy(url_name, kwargs=kwargs))
    else:
        referer = request.META.get("HTTP_REFERER")
        if referer and url_has_allowed_host_and_scheme(
            referer,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            action = referer
        else:
            action = "/"

    params = {k: v for k, v in request.GET.items() if k not in ("submit", "ref")}
    if params:
        delimiter = "&" if "?" in action else "?"
        action += delimiter + urlencode(params)
    return action
