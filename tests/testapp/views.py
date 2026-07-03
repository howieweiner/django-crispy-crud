from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView

from crispy_crud.views.mixins import (
    BaseModelAppMixin,
    CrispyFormArgsMixin,
    FilterFormMixin,
    HtmxFilterListMixin,
)

from .filters import WidgetFilter
from .forms import WidgetFilterForm, WidgetForm
from .models import Widget


class WidgetListView(BaseModelAppMixin, FilterFormMixin, HtmxFilterListMixin, FilterView):
    model = Widget
    filterset_class = WidgetFilter
    template_name = "testapp/widget_list.html"
    partial_template_name = "testapp/fragments/widget_table.html"
    section = "widget-list"
    create_view_name = "widget-create"
    filter_form_class = WidgetFilterForm


class WidgetCreateView(SuccessMessageMixin, BaseModelAppMixin, CrispyFormArgsMixin, CreateView):
    model = Widget
    form_class = WidgetForm
    template_name = "testapp/widget_detail.html"
    section = "widgets"
    success_url = reverse_lazy("widget-list")
    success_message = "Widget created successfully"


class WidgetUpdateView(SuccessMessageMixin, BaseModelAppMixin, CrispyFormArgsMixin, UpdateView):
    model = Widget
    form_class = WidgetForm
    template_name = "testapp/widget_detail.html"
    section = "widgets"
    delete_view_name = "widget-delete"
    success_url = reverse_lazy("widget-list")
    success_message = "Widget updated successfully"


class WidgetDeleteView(BaseModelAppMixin, DeleteView):
    model = Widget
    template_name = "testapp/widget_confirm_delete.html"
    section = "widgets"
    success_url = reverse_lazy("widget-list")
