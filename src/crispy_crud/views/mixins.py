from __future__ import annotations

from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import ProgrammingError
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django_filters.views import FilterView
from django_htmx.http import push_url

from ..conf import get_setting
from ..utils.url_utils import remove_empty_url_params
from .utils import add_page_context_data

ONE_YEAR_IN_SECONDS = 31536000


class PaginationMixin:
    paginate_by = None
    cookie_name = "paginate_by"
    param_name = "paginate_by"

    def get_default_page_size(self):
        return self.paginate_by or get_setting("CRISPY_CRUD_PAGINATE_BY")

    def get_paginate_by(self, queryset):
        page_size = self.request.GET.get(self.param_name)
        if page_size:
            return page_size
        elif self.cookie_name in self.request.COOKIES:
            return int(self.request.COOKIES[self.cookie_name])
        return self.get_default_page_size()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size = self.request.GET.get(self.param_name)
        if page_size:
            context["page_size"] = page_size
        elif self.cookie_name in self.request.COOKIES:
            context["page_size"] = self.request.COOKIES[self.cookie_name]
        else:
            context["page_size"] = self.get_default_page_size()
        context["page_size_options"] = get_setting("CRISPY_CRUD_PAGE_SIZE_OPTIONS")
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        page_size = context.get("page_size", self.get_default_page_size())
        response.set_cookie(self.cookie_name, page_size, max_age=ONE_YEAR_IN_SECONDS)
        return response


class HtmxPaginationMixin(PaginationMixin):
    """
    If the request is HTMX, push the URL to the browser with the
    page size params.
    """

    def get(self, request, *args, **kwargs):
        if request.htmx:
            if not hasattr(self, "view_name"):
                raise ValueError("Htmx view name is not set")
            response = super().get(request, *args, **kwargs)
            query_dict = request.GET.copy()
            clean_query_dict = self._clean_pagination_params(query_dict)
            clean_query_string = urlencode(clean_query_dict)
            return push_url(
                response,
                reverse(self.view_name) + "?" + clean_query_string,
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_dict = self.request.GET.copy()
        if "page" in query_dict:
            query_dict.pop("page")
        context["pagination_query_params"] = urlencode(query_dict)
        return context

    def _clean_pagination_params(self, query_dict):
        if "page" in query_dict:
            page_value = query_dict.get("page")
            if isinstance(page_value, list):
                query_dict["page"] = page_value[-1]
        return query_dict


class CrispyFormArgsMixin:
    """Mixin that adds request to form kwargs."""

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["request"] = self.request
        return kw


class BaseAppMixin:
    heading = None
    section = None

    def _get_heading(self):
        return self.heading

    def _get_section(self):
        if not self.section:
            raise ValueError("BaseAppMixin:  section is not set")
        return self.section

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_page_context_data(context=context, section=self._get_section(), heading=self._get_heading())


class BaseModelAppMixin(BaseAppMixin):
    delete_view_name = None

    def _get_heading(self):
        if isinstance(self, (ListView, FilterView)):
            return self.model._meta.verbose_name_plural
        elif isinstance(self, CreateView):
            return f"Add {self.model._meta.verbose_name}"
        elif isinstance(self, UpdateView):
            return f"Update {self.model._meta.verbose_name}"
        else:
            return self.heading

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = add_page_context_data(
            context=context,
            section=self._get_section(),
            heading=self._get_heading(),
            model_name=self.model._meta.verbose_name,
        )

        if isinstance(self, (ListView, FilterView)):
            create_view_name = self.get_create_view_name()
            if create_view_name:
                context["create_action"] = reverse(create_view_name)

        if isinstance(self, UpdateView):
            delete_view_name = self.get_delete_view_name()
            context["delete_action"] = reverse(delete_view_name, args=[self.object.pk]) if delete_view_name else None
            context["can_delete"] = not self._has_related_objects()
        return context

    def get_success_message(self, _):
        if isinstance(self, CreateView):
            return f"{self.model._meta.verbose_name} created successfully"
        elif isinstance(self, UpdateView):
            return f"{self.model._meta.verbose_name} updated successfully"
        elif isinstance(self, DeleteView):
            return f"{self.model._meta.verbose_name} deleted successfully"
        return None

    def get_create_view_name(self):
        return self.create_view_name if hasattr(self, "create_view_name") else None

    def get_delete_view_name(self):
        return self.delete_view_name

    def get_success_url(self):
        url = super().get_success_url()
        if url:
            url = f"{url}?{self.request.GET.urlencode()}"
        return url

    def _has_related_objects(self):
        for relation in self.model._meta.related_objects:
            if relation.one_to_one:
                try:
                    getattr(self.object, relation.get_accessor_name())
                    return True
                except Exception:
                    continue
            else:
                related_manager = getattr(self.object, relation.get_accessor_name())
                try:
                    if related_manager.exists():
                        return True
                except ProgrammingError:
                    continue
        return False


class HtmxFilterListMixin(PaginationMixin):
    """Switches to partial template on HTMX requests and pushes URL."""

    partial_template_name = None

    def _get_partial_template_name(self):
        if not self.partial_template_name:
            raise ValueError("FilterListMixin:  partial_template_name is not set")
        return self.partial_template_name

    def get(self, request, *args, **kwargs):
        if request.htmx:
            self.template_name = self._get_partial_template_name()
            response = super().get(request, *args, **kwargs)
            url_params = remove_empty_url_params(request.GET.urlencode())
            return push_url(
                response,
                reverse_lazy(self._get_section()) + "?" + url_params,
            )
        return super().get(request, *args, **kwargs)


class FilterFormMixin:
    """Places a populated filter form in the context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form_class = self.get_filter_form_class()
        filter_form = filter_form_class(initial=self.request.GET.dict())
        context["filter_form"] = filter_form
        filter_fields = [field for field in filter_form.fields.keys() if field != "q"]
        context["filter_fields"] = filter_fields
        context["query_params"] = urlencode(self.request.GET.dict())
        return context

    def get_filter_form_class(self):
        if not hasattr(self, "filter_form_class"):
            raise ValueError("filter_form_class attribute is not set")
        return self.filter_form_class


class AuditLogMixin:
    """Provides paginated audit history for an object."""

    audit_template_name = "crispy_crud/fragments/details/audit_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history_list = self.object.history.all()
        page_size = get_setting("CRISPY_CRUD_AUDIT_PAGE_SIZE")
        paginator = Paginator(history_list, page_size)
        page = self.request.GET.get("audit_page", 1)
        history = paginator.get_page(page)
        context["history"] = history
        return context

    def get(self, request, *args, **kwargs):
        if request.htmx:
            self.template_name = self.audit_template_name
            response = super().get(request, *args, **kwargs)
            url_params = request.GET.urlencode()
            return push_url(
                response,
                self.get_object().get_absolute_url() + "?" + url_params,
            )
        return super().get(request, *args, **kwargs)
