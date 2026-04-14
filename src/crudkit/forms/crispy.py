from urllib.parse import urlencode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, ButtonHolder, Field, Layout
from crispy_tailwind.layout import Submit

from ..views.utils import get_cancel_url


class AlpineSubmit(Submit):
    """Submit button with Alpine.js attribute support."""

    def __init__(self, *args, **kwargs):
        self.alpine_attrs = kwargs.pop("alpine_attrs", {})
        super().__init__(*args, **kwargs)

    def render(self, form, context, template_pack="bootstrap4"):
        button_html = super().render(form, context, template_pack)
        for attr, value in self.alpine_attrs.items():
            button_html = button_html.replace(">", f' {attr}="{value}">', 1)
        return button_html


class CrispyFormMixin:
    submit_button_text = "Save"
    cancel_action = None
    full_width = True
    button_holder_css = "mt-8 h-24 border-t border-gray-900/10 flex justify-end items-center space-x-8 w_full"
    button_holder_width = ""

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_action = self.request.path if self.request else ""

        params = self.request.GET.dict() if self.request else {}
        params = urlencode(params)
        self.helper.form_action += f"?{params}"

        self.helper.label_class = "block text-sm/6 font-medium text-gray-900"

        if not self.full_width:
            self.button_holder_width = " md:w-2/3"

        self.button_holder = Layout(
            ButtonHolder(
                HTML(f'<a href="{self.cancel_link}" class="form-link" id="cancel-btn">Cancel</a>'),
                AlpineSubmit(
                    "submit",
                    self.get_submit_button_text(),
                    css_class="btn-primary",
                    alpine_attrs={
                        ":disabled": "!isDirty",
                        ":class": "{'btn-disabled': !isDirty}",
                    },
                ),
                css_class=self.button_holder_css + self.button_holder_width,
            )
        )

        self.readonly_button_holder = Layout(
            ButtonHolder(
                HTML(f'<a href="{self.cancel_link}" class="form-link" id="cancel-btn">Cancel</a>'),
                css_class=self.button_holder_css + self.button_holder_width,
            )
        )

    def get_submit_button_text(self):
        return self.submit_button_text

    @property
    def cancel_link(self):
        return get_cancel_url(self.request, self.cancel_action)


class BaseFilterFormHelper(FormHelper):
    form_tag = False
    form_action = ""
    form_method = "GET"
    label_class = "block text-sm/6 font-medium text-gray-900"
    field_class = "mb-0"
    q_field_placeholder = "Search"

    form_css = "grid grid-cols-1 sm:grid-cols-2 lg:flex lg:flex-wrap gap-4 items-end mb-4"

    q_field = Field(
        "q",
        data_lpignore="true",
        placeholder=q_field_placeholder,
        wrapper_class="w-72",
    )

    button_holder = ButtonHolder(
        HTML('<a href="?" class="form-link">Reset</a>'),
        css_class="flex space-x-4",
    )

    def get_q_field_placeholder(self):
        return self.q_field_placeholder

    def __init__(self):
        super().__init__()
        self.attrs = {"autocomplete": "off"}
