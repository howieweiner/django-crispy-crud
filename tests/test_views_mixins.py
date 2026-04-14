import pytest
from django.test import RequestFactory
from django.views.generic import ListView, CreateView, UpdateView

from crudkit.views.mixins import (
    PaginationMixin,
    HtmxPaginationMixin,
    CrispyFormArgsMixin,
    BaseAppMixin,
    BaseModelAppMixin,
    HtmxFilterListMixin,
    FilterFormMixin,
    AuditLogMixin,
)

from tests.testapp.models import Widget, Gadget
from tests.testapp.forms import WidgetForm, WidgetFilterForm


pytestmark = pytest.mark.django_db


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def widget():
    return Widget.objects.create(name="Test Widget", description="A test widget")


@pytest.fixture
def widget_with_gadget(widget):
    Gadget.objects.create(widget=widget, name="Test Gadget")
    return widget


# --- PaginationMixin ---


class PaginatedListView(PaginationMixin, ListView):
    model = Widget
    template_name = "testapp/widget_list.html"


class TestPaginationMixin:
    def test_default_paginate_by(self, rf):
        request = rf.get("/")
        view = PaginatedListView()
        view.request = request
        assert view.get_paginate_by(Widget.objects.none()) == 25

    def test_paginate_by_from_query_param(self, rf):
        request = rf.get("/", {"paginate_by": "50"})
        view = PaginatedListView()
        view.request = request
        assert view.get_paginate_by(Widget.objects.none()) == "50"

    def test_paginate_by_from_cookie(self, rf):
        request = rf.get("/")
        request.COOKIES["paginate_by"] = "10"
        view = PaginatedListView()
        view.request = request
        assert view.get_paginate_by(Widget.objects.none()) == 10

    def test_query_param_takes_precedence_over_cookie(self, rf):
        request = rf.get("/", {"paginate_by": "50"})
        request.COOKIES["paginate_by"] = "10"
        view = PaginatedListView()
        view.request = request
        assert view.get_paginate_by(Widget.objects.none()) == "50"

    def test_page_size_in_context(self, rf):
        request = rf.get("/", {"paginate_by": "50"})
        view = PaginatedListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["page_size"] == "50"

    def test_page_size_cookie_default_in_context(self, rf):
        request = rf.get("/")
        view = PaginatedListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["page_size"] == 25

    def test_sets_cookie_on_response(self, rf):
        request = rf.get("/")
        view = PaginatedListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        response = view.render_to_response(view.get_context_data())
        assert "paginate_by" in response.cookies

    def test_page_size_options_in_context(self, rf):
        request = rf.get("/")
        view = PaginatedListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["page_size_options"] == [10, 25, 50, 100]

    def test_page_size_options_override(self, rf, settings):
        settings.CRUDKIT_PAGE_SIZE_OPTIONS = [5, 10, 20]
        request = rf.get("/")
        view = PaginatedListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["page_size_options"] == [5, 10, 20]


# --- CrispyFormArgsMixin ---


class CrispyCreateView(CrispyFormArgsMixin, CreateView):
    model = Widget
    form_class = WidgetForm
    template_name = "testapp/widget_detail.html"


class TestCrispyFormArgsMixin:
    def test_request_in_form_kwargs(self, rf):
        request = rf.get("/")
        view = CrispyCreateView()
        view.request = request
        view.kwargs = {}
        view.object = None
        kwargs = view.get_form_kwargs()
        assert "request" in kwargs
        assert kwargs["request"] is request


# --- BaseAppMixin ---


class BaseListView(BaseAppMixin, ListView):
    model = Widget
    template_name = "testapp/widget_list.html"
    section = "widgets"
    heading = "All Widgets"


class TestBaseAppMixin:
    def test_section_required(self, rf):
        class NoSectionView(BaseAppMixin, ListView):
            model = Widget
            template_name = "testapp/widget_list.html"

        request = rf.get("/")
        view = NoSectionView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        with pytest.raises(ValueError, match="section is not set"):
            view.get_context_data()

    def test_context_has_heading_and_section(self, rf):
        request = rf.get("/")
        view = BaseListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["heading"] == "All Widgets"
        assert context["section"] == "widgets"


# --- BaseModelAppMixin ---


class ModelListView(BaseModelAppMixin, ListView):
    model = Widget
    template_name = "testapp/widget_list.html"
    section = "widgets"
    create_view_name = "widget-create"


class ModelCreateView(BaseModelAppMixin, CreateView):
    model = Widget
    form_class = WidgetForm
    template_name = "testapp/widget_detail.html"
    section = "widgets"
    success_url = "/widgets/"


class ModelUpdateView(BaseModelAppMixin, UpdateView):
    model = Widget
    form_class = WidgetForm
    template_name = "testapp/widget_detail.html"
    section = "widgets"
    delete_view_name = "widget-delete"
    success_url = "/widgets/"


class TestBaseModelAppMixin:
    def test_list_view_heading_uses_verbose_name_plural(self, rf):
        request = rf.get("/")
        view = ModelListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["heading"] == "widgets"

    def test_create_view_heading(self, rf):
        request = rf.get("/")
        view = ModelCreateView()
        view.request = request
        view.object = None
        view.kwargs = {}
        context = view.get_context_data()
        assert context["heading"] == "Add widget"

    def test_update_view_heading(self, rf, widget):
        request = rf.get("/")
        view = ModelUpdateView()
        view.request = request
        view.object = widget
        view.kwargs = {"pk": widget.pk}
        context = view.get_context_data()
        assert context["heading"] == "Update widget"

    def test_list_view_has_create_action(self, rf):
        request = rf.get("/")
        view = ModelListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert context["create_action"] == "/widgets/create/"

    def test_update_view_has_delete_action(self, rf, widget):
        request = rf.get("/")
        view = ModelUpdateView()
        view.request = request
        view.object = widget
        view.kwargs = {"pk": widget.pk}
        context = view.get_context_data()
        assert context["delete_action"] == f"/widgets/{widget.pk}/delete/"

    def test_can_delete_when_no_related_objects(self, rf, widget):
        request = rf.get("/")
        view = ModelUpdateView()
        view.request = request
        view.object = widget
        view.kwargs = {"pk": widget.pk}
        context = view.get_context_data()
        assert context["can_delete"] is True

    def test_cannot_delete_when_has_related_objects(self, rf, widget_with_gadget):
        request = rf.get("/")
        view = ModelUpdateView()
        view.request = request
        view.object = widget_with_gadget
        view.kwargs = {"pk": widget_with_gadget.pk}
        context = view.get_context_data()
        assert context["can_delete"] is False

    def test_success_message_create(self, rf):
        view = ModelCreateView()
        assert view.get_success_message(None) == "widget created successfully"

    def test_success_message_update(self, rf):
        view = ModelUpdateView()
        assert view.get_success_message(None) == "widget updated successfully"

    def test_success_url_includes_query_params(self, rf, widget):
        request = rf.get("/", {"is_active": "true"})
        view = ModelUpdateView()
        view.request = request
        view.object = widget
        view.kwargs = {"pk": widget.pk}
        url = view.get_success_url()
        assert "is_active=true" in url


# --- FilterFormMixin ---


class FilterFormListView(FilterFormMixin, ListView):
    model = Widget
    template_name = "testapp/widget_list.html"
    filter_form_class = WidgetFilterForm


class TestFilterFormMixin:
    def test_filter_form_in_context(self, rf):
        request = rf.get("/", {"is_active": "true"})
        view = FilterFormListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert "filter_form" in context
        assert isinstance(context["filter_form"], WidgetFilterForm)

    def test_filter_fields_excludes_q(self, rf):
        request = rf.get("/")
        view = FilterFormListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert "q" not in context["filter_fields"]
        assert "is_active" in context["filter_fields"]

    def test_query_params_in_context(self, rf):
        request = rf.get("/", {"q": "test", "is_active": "true"})
        view = FilterFormListView()
        view.request = request
        view.object_list = Widget.objects.none()
        view.kwargs = {}
        context = view.get_context_data()
        assert "query_params" in context

    def test_missing_filter_form_class_raises(self, rf):
        class BadView(FilterFormMixin, ListView):
            model = Widget
            template_name = "testapp/widget_list.html"

        view = BadView()
        with pytest.raises(ValueError, match="filter_form_class"):
            view.get_filter_form_class()
