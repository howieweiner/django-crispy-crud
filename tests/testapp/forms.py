from django import forms

from crispy_forms.layout import Field, Layout

from crispy_crud.forms.crispy import BaseFilterFormHelper, CrispyFormMixin

from .models import Widget


class WidgetForm(CrispyFormMixin, forms.ModelForm):
    cancel_action = "widget-list"

    class Meta:
        model = Widget
        fields = ["name", "description", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Field("name"),
            Field("description"),
            Field("is_active"),
            self.button_holder,
        )


class WidgetFilterFormHelper(BaseFilterFormHelper):
    q_field_placeholder = "Search widgets..."

    def __init__(self):
        super().__init__()
        self.form_class = self.form_css
        self.layout = Layout(
            self.q_field,
            Field("is_active", wrapper_class="w-40"),
            self.button_holder,
        )


class WidgetFilterForm(forms.Form):
    q = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = WidgetFilterFormHelper()
