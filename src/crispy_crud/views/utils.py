from __future__ import annotations

from django.http import HttpRequest
from django.urls import reverse_lazy


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
    Falls back to request referrer if url_name is not provided.
    """
    if request is None:
        return None

    if url_name:
        action = str(reverse_lazy(url_name, kwargs=kwargs))
    else:
        action = request.META.get("HTTP_REFERER") or "javascript:history.back()"

    for k, v in request.GET.items():
        if k not in ("submit", "ref"):
            delimiter = "&" if "?" in action else "?"
            action += f"{delimiter}{k}={v}"
    return action
