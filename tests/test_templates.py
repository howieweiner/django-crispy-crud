import pytest
from django.template import Template, Context, engines


pytestmark = pytest.mark.django_db


class TestFragmentTemplatesRender:
    """Each fragment renders without errors given appropriate context."""

    def _render(self, template_name, context_dict=None):
        engine = engines["django"]
        template = engine.get_template(template_name)
        ctx = context_dict or {}
        return template.render(ctx)

    def test_success_alert(self):
        html = self._render("crispy_crud/fragments/common/success_alert.html", {"message": "Saved!"})
        assert "Saved!" in html
        assert "bg-green-200" in html

    def test_error_alert(self):
        html = self._render("crispy_crud/fragments/common/error_alert.html", {"message": "Failed!"})
        assert "Failed!" in html
        assert "bg-red-200" in html

    def test_page_heading(self):
        html = self._render("crispy_crud/fragments/common/page_heading.html", {"heading": "Widgets"})
        assert "Widgets" in html

    def test_page_heading_with_sub(self):
        html = self._render(
            "crispy_crud/fragments/common/page_heading.html",
            {"heading": "Widgets", "sub_heading": "Active"},
        )
        assert "Widgets" in html
        assert "Active" in html

    def test_page_heading_empty(self):
        html = self._render("crispy_crud/fragments/common/page_heading.html", {})
        assert html.strip() == ""

    def test_table_heading(self):
        html = self._render(
            "crispy_crud/fragments/table/table_heading.html",
            {"text": "Name", "first_column": True},
        )
        assert "Name" in html
        assert "<th" in html

    def test_table_cell(self):
        html = self._render(
            "crispy_crud/fragments/table/table_cell.html",
            {"text": "Widget A", "first_column": True},
        )
        assert "Widget A" in html
        assert "<td" in html

    def test_table_cell_strong(self):
        html = self._render(
            "crispy_crud/fragments/table/table_cell.html",
            {"text": "Bold", "strong": True, "first_column": True},
        )
        assert "font-medium" in html

    def test_table_cell_align_right(self):
        html = self._render(
            "crispy_crud/fragments/table/table_cell.html",
            {"text": "100", "align": "right", "first_column": True},
        )
        assert "text-right" in html

    def test_delete_action_can_delete(self):
        html = self._render(
            "crispy_crud/fragments/details/delete_action.html",
            {"can_delete": True, "delete_action": "/delete/1/", "model_name": "widget"},
        )
        assert "Delete" in html
        assert "showConfirm" in html
        assert "/delete/1/" in html

    def test_delete_action_cannot_delete(self):
        html = self._render(
            "crispy_crud/fragments/details/delete_action.html",
            {"can_delete": False, "model_name": "widget"},
        )
        assert "cannot be deleted" in html
        assert "showConfirm" not in html

    def test_form_field_error(self):
        html = self._render(
            "crispy_crud/fragments/forms/form_field_error.html",
            {"error_key": ["This field is required."]},
        )
        assert "This field is required." in html
        assert "text-red-600" in html

    def test_form_field_error_empty(self):
        html = self._render("crispy_crud/fragments/forms/form_field_error.html", {})
        assert html.strip() == ""

    def test_read_only_field(self):
        html = self._render(
            "crispy_crud/fragments/forms/read_only_field.html",
            {"label": "Name", "value": "Widget A"},
        )
        assert "Name" in html
        assert "Widget A" in html

    def test_read_only_form_field(self):
        html = self._render(
            "crispy_crud/fragments/forms/read_only_form_field.html",
            {"label": "Name", "value": "Widget A"},
        )
        assert "Name" in html
        assert "disabled" in html

    def test_read_only_checkbox_checked(self):
        html = self._render(
            "crispy_crud/fragments/forms/read_only_checkbox.html",
            {"label": "Active", "value": True},
        )
        assert "Active" in html
        assert "checked" in html

    def test_read_only_checkbox_unchecked(self):
        html = self._render(
            "crispy_crud/fragments/forms/read_only_checkbox.html",
            {"label": "Active", "value": False},
        )
        assert "Active" in html
        assert "translate-x-0" in html

    def test_loading_spinner(self):
        html = self._render("crispy_crud/fragments/loaders/loading_spinner.html")
        assert "htmx-indicator" in html
        assert "animate-spin" in html

    def test_busy_indicator(self):
        html = self._render("crispy_crud/fragments/loaders/busy_indicator.html")
        assert "Busy.." in html

    def test_busy_indicator_custom_message(self):
        html = self._render("crispy_crud/fragments/loaders/busy_indicator.html", {"message": "Loading..."})
        assert "Loading..." in html

    def test_submit_cancel(self):
        class FakeForm:
            cancel_link = "/widgets/"

        html = self._render("crispy_crud/fragments/forms/submit_cancel.html", {"form": FakeForm()})
        assert "/widgets/" in html
        assert "Save" in html

    def test_hx_add_model_oob_link(self):
        html = self._render(
            "crispy_crud/fragments/table/hx_add_model_oob_link.html",
            {"is_htmx": True, "create_action": "/widgets/create/", "query_params": "q=test", "model_name": "widget"},
        )
        assert "hx-swap-oob" in html
        assert "Add Widget" in html

    def test_hx_add_model_oob_link_not_htmx(self):
        html = self._render(
            "crispy_crud/fragments/table/hx_add_model_oob_link.html",
            {"is_htmx": False},
        )
        assert html.strip() == ""


class TestTemplateTag:
    def test_filter_form_fields_returns_trigger_string(self):
        from django import forms

        class TestFilterForm(forms.Form):
            q = forms.CharField(required=False)
            is_active = forms.BooleanField(required=False)
            category = forms.CharField(required=False)

        t = Template("{% load crispy_crud_tags %}{% filter_form_fields %}")
        ctx = Context({"filter_form": TestFilterForm()})
        result = t.render(ctx)
        assert "change from:[name='is_active']" in result
        assert "change from:[name='category']" in result
        assert "q" not in result.replace("change from", "")  # q should be excluded

    def test_filter_form_fields_empty_form(self):
        from django import forms

        class EmptyFilterForm(forms.Form):
            q = forms.CharField(required=False)

        t = Template("{% load crispy_crud_tags %}{% filter_form_fields %}")
        ctx = Context({"filter_form": EmptyFilterForm()})
        result = t.render(ctx)
        assert result.strip() == ""

    def test_filter_form_fields_no_form(self):
        t = Template("{% load crispy_crud_tags %}{% filter_form_fields %}")
        ctx = Context({})
        result = t.render(ctx)
        assert result.strip() == ""
