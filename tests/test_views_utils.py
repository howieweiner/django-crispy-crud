import pytest
from django.test import RequestFactory

from crispy_crud.views.utils import add_page_context_data, get_cancel_url


@pytest.fixture
def rf():
    return RequestFactory()


class TestAddPageContextData:
    def test_adds_section_and_heading(self):
        context = {}
        result = add_page_context_data(context, section="widgets", heading="All Widgets")
        assert result["section"] == "widgets"
        assert result["heading"] == "All Widgets"

    def test_adds_model_name(self):
        context = {}
        result = add_page_context_data(context, section="widgets", model_name="widget")
        assert result["model_name"] == "widget"

    def test_preserves_existing_context(self):
        context = {"existing_key": "existing_value"}
        result = add_page_context_data(context, section="widgets")
        assert result["existing_key"] == "existing_value"
        assert result["section"] == "widgets"


class TestGetCancelUrl:
    def test_returns_none_when_no_request(self):
        assert get_cancel_url(None, "widget-list") is None

    def test_returns_named_url(self, rf):
        request = rf.get("/")
        url = get_cancel_url(request, "widget-list")
        assert url == "/widgets/"

    def test_appends_query_params(self, rf):
        request = rf.get("/", {"is_active": "true"})
        url = get_cancel_url(request, "widget-list")
        assert "is_active=true" in url

    def test_excludes_submit_and_ref_params(self, rf):
        request = rf.get("/", {"submit": "1", "ref": "somewhere", "is_active": "true"})
        url = get_cancel_url(request, "widget-list")
        assert "submit" not in url
        assert "ref" not in url
        assert "is_active=true" in url

    def test_falls_back_to_referrer(self, rf):
        request = rf.get("/", HTTP_REFERER="/previous-page/")
        url = get_cancel_url(request, None)
        assert url == "/previous-page/"

    def test_falls_back_to_history_back(self, rf):
        request = rf.get("/")
        url = get_cancel_url(request, None)
        assert "history.back()" in url
