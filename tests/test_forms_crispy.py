import pytest
from django.forms import ModelForm
from django.template import Context
from django.test import RequestFactory

from crispy_crud.forms.crispy import AlpineSubmit, CrispyFormMixin, BaseFilterFormHelper
from tests.testapp.models import Widget


@pytest.fixture
def rf():
    return RequestFactory()


# --- AlpineSubmit ---


class TestAlpineSubmit:
    def test_renders_button(self):
        btn = AlpineSubmit("submit", "Save", css_class="btn-primary")
        html = btn.render(form=None, context=Context(), template_pack="tailwind")
        assert "Save" in html
        assert 'type="submit"' in html

    def test_renders_alpine_attrs(self):
        btn = AlpineSubmit(
            "submit",
            "Save",
            alpine_attrs={":disabled": "!isDirty", ":class": "{'btn-disabled': !isDirty}"},
        )
        html = btn.render(form=None, context=Context(), template_pack="tailwind")
        assert ":disabled" in html
        assert "!isDirty" in html


# --- CrispyFormMixin ---


class WidgetCrispyForm(CrispyFormMixin, ModelForm):
    cancel_action = "widget-list"

    class Meta:
        model = Widget
        fields = ["name", "description", "is_active"]


class TestCrispyFormMixin:
    def test_initializes_with_request(self, rf):
        request = rf.get("/widgets/1/")
        form = WidgetCrispyForm(request=request)
        assert form.request is request
        assert form.helper is not None

    def test_form_action_includes_request_path(self, rf):
        request = rf.get("/widgets/1/")
        form = WidgetCrispyForm(request=request)
        assert "/widgets/1/" in form.helper.form_action

    def test_form_action_includes_query_params(self, rf):
        request = rf.get("/widgets/1/", {"is_active": "true"})
        form = WidgetCrispyForm(request=request)
        assert "is_active=true" in form.helper.form_action

    def test_cancel_link_resolves(self, rf):
        request = rf.get("/widgets/1/")
        form = WidgetCrispyForm(request=request)
        assert "/widgets/" in form.cancel_link

    def test_submit_button_text_default(self, rf):
        request = rf.get("/")
        form = WidgetCrispyForm(request=request)
        assert form.get_submit_button_text() == "Save"

    def test_submit_button_text_override(self, rf):
        class CustomForm(CrispyFormMixin, ModelForm):
            submit_button_text = "Create"
            cancel_action = "widget-list"

            class Meta:
                model = Widget
                fields = ["name"]

        request = rf.get("/")
        form = CustomForm(request=request)
        assert form.get_submit_button_text() == "Create"

    def test_initializes_without_request(self):
        form = WidgetCrispyForm()
        assert form.request is None
        assert form.helper.form_action == "?"

    def test_has_button_holder(self, rf):
        request = rf.get("/")
        form = WidgetCrispyForm(request=request)
        assert form.button_holder is not None

    def test_has_readonly_button_holder(self, rf):
        request = rf.get("/")
        form = WidgetCrispyForm(request=request)
        assert form.readonly_button_holder is not None

    def test_narrow_width(self, rf):
        class NarrowForm(CrispyFormMixin, ModelForm):
            full_width = False
            cancel_action = "widget-list"

            class Meta:
                model = Widget
                fields = ["name"]

        request = rf.get("/")
        form = NarrowForm(request=request)
        assert "md:w-2/3" in form.button_holder_width


# --- BaseFilterFormHelper ---


class TestBaseFilterFormHelper:
    def test_initializes(self):
        helper = BaseFilterFormHelper()
        assert helper.form_tag is False
        assert helper.form_method == "GET"

    def test_has_autocomplete_off(self):
        helper = BaseFilterFormHelper()
        assert helper.attrs["autocomplete"] == "off"

    def test_q_field_placeholder_default(self):
        helper = BaseFilterFormHelper()
        assert helper.get_q_field_placeholder() == "Search"

    def test_q_field_placeholder_override(self):
        class CustomHelper(BaseFilterFormHelper):
            q_field_placeholder = "Filter widgets..."

        helper = CustomHelper()
        assert helper.get_q_field_placeholder() == "Filter widgets..."
