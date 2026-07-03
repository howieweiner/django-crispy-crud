# django-crispy-crud

[![PyPI version](https://img.shields.io/pypi/v/django-crispy-crud.svg)](https://pypi.org/project/django-crispy-crud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/howieweiner/django-crispy-crud/blob/main/LICENSE)

Reusable Django CRUD views, forms, and template fragments with HTMX, Alpine.js, and Tailwind CSS.

## Installation

**With uv:**

```bash
uv add django-crispy-crud
```

**With pip:**

```bash
pip install django-crispy-crud
```

For audit log support (optional):

```bash
uv add "django-crispy-crud[audit]"
# or
pip install "django-crispy-crud[audit]"
```

## Setup

Add `crispy_crud` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_tailwind",
    "django_htmx",
    "django_filters",
    "crispy_crud",
]
```

Add the required middleware:

```python
MIDDLEWARE = [
    # ...
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]
```

Ensure the messages context processor is included in your template settings:

```python
TEMPLATES = [
    {
        # ...
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                # ...
            ],
        },
    },
]
```

Set crispy forms to use Tailwind:

```python
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
```

Your base template must load Alpine.js and HTMX (not bundled):

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.0"></script>
```

### Component CSS

The package templates use custom CSS classes (`btn-primary`, `btn-secondary`, `btn-important`, `btn-disabled`, `form-link`, `readonly-form-field`, `toggle`). A reference stylesheet is provided at `static/crispy_crud/css/components.css` using Tailwind `@apply` directives.

Add it to your Tailwind CSS input file:

```css
@import "../../static/crispy_crud/css/components.css";
```

Or copy the definitions into your own CSS. See the test app's `base.html` for a working example.

## Usage

### View mixins

```python
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from crispy_crud.views import (
    BaseModelAppMixin, CrispyFormArgsMixin,
    FilterFormMixin, HtmxFilterListMixin,
)

class WidgetListView(BaseModelAppMixin, FilterFormMixin, HtmxFilterListMixin, FilterView):
    model = Widget
    filterset_class = WidgetFilter
    template_name = "myapp/widget_list.html"
    partial_template_name = "myapp/fragments/widget_table.html"
    section = "widget-list"
    create_view_name = "widget-create"
    filter_form_class = WidgetFilterForm

class WidgetUpdateView(BaseModelAppMixin, CrispyFormArgsMixin, UpdateView):
    model = Widget
    form_class = WidgetForm
    template_name = "myapp/widget_detail.html"
    section = "widgets"
    delete_view_name = "widget-delete"
    success_url = reverse_lazy("widget-list")
```

### Form helpers

```python
from django import forms
from crispy_crud.forms import CrispyFormMixin

class WidgetForm(CrispyFormMixin, forms.ModelForm):
    cancel_action = "widget-list"

    class Meta:
        model = Widget
        fields = ["name", "description", "is_active"]
```

`CrispyFormMixin` provides a crispy `FormHelper`, cancel link, and Alpine.js dirty-state submit button out of the box. You need to set the layout in your form's `__init__` and include `self.button_holder` at the end:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.helper.layout = Layout(
        Field("name"),
        Field("description"),
        Field("is_active"),
        self.button_holder,
    )
```

### Filter forms

Create a filter form with a crispy helper using `BaseFilterFormHelper`:

```python
from crispy_crud.forms import BaseFilterFormHelper
from crispy_forms.layout import Field, Layout

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
```

Set `filter_form_class` on your list view, and include the HTMX filter form fragment in your list template:

```html
{% include 'crispy_crud/fragments/forms/hx_filter_form.html' with view_name="widget-list" %}
```

This renders a form that auto-submits via HTMX on input changes -- the search field fires after a 500ms debounce, and select/checkbox fields fire on change. The `filter_form_fields` template tag automatically generates the correct HTMX trigger selectors for your filter fields.

You also need a `django-filter` `FilterSet` on your view:

```python
import django_filters

class WidgetFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Widget
        fields = ["q", "is_active"]
```

### Template fragments

The package provides reusable template fragments under `crispy_crud/fragments/`. Include them in your own templates:

```html
{% include 'crispy_crud/fragments/common/messages.html' %}
{% include 'crispy_crud/fragments/common/page_heading.html' %}
{% include 'crispy_crud/fragments/table/table_heading.html' with text="Name" first_column=True %}
{% include 'crispy_crud/fragments/table/table_cell.html' with text=widget.name first_column=True %}
{% include 'crispy_crud/fragments/table/hx_pagination.html' with page=page_obj %}
{% include 'crispy_crud/fragments/details/delete_action.html' %}
{% include 'crispy_crud/fragments/loaders/loading_spinner.html' %}
```

### Static files

Include the Alpine.js components for form state tracking and pagination:

```html
<script src="{% static 'crispy_crud/js/formState.js' %}"></script>
<script src="{% static 'crispy_crud/js/pagination.js' %}"></script>
```

## Configuration

All settings are optional and have sensible defaults:

| Setting | Default | Purpose |
|---|---|---|
| `CRISPY_CRUD_PAGINATE_BY` | `25` | Default page size |
| `CRISPY_CRUD_PAGE_SIZE_OPTIONS` | `[10, 25, 50, 100]` | Page-size pills shown in pagination |
| `CRISPY_CRUD_AUDIT_PAGE_SIZE` | `25` | Rows per page in audit history table |

## Running the test app

The test app in `tests/testapp/` is a working example you can clone as a starting point. To run it locally:

```bash
git clone https://github.com/howieweiner/django-crispy-crud.git
cd django-crispy-crud
uv run python manage.py migrate
uv run python manage.py runserver
```

Then visit http://localhost:8000/widgets/ to see the list view with filtering, pagination, create/update forms, and delete with confirmation modal.

## Development

```bash
uv run pytest                    # run tests
uv run ruff check src/ tests/    # lint
uv run ruff format src/ tests/   # format
```

## What's included

### View mixins (`crispy_crud.views`)
- **PaginationMixin** -- page size from query param, cookie, or config
- **HtmxPaginationMixin** -- extends PaginationMixin with HTMX URL push
- **CrispyFormArgsMixin** -- injects `request` into form kwargs
- **BaseAppMixin** -- section/heading context
- **BaseModelAppMixin** -- auto-generated headings, create/delete actions, related-object protection
- **HtmxFilterListMixin** -- switches to partial template on HTMX requests
- **FilterFormMixin** -- populates filter form in context
- **AuditLogMixin** -- paginated audit history (requires `django-auditlog`)

### Form helpers (`crispy_crud.forms`)
- **CrispyFormMixin** -- crispy FormHelper with cancel link and Alpine.js dirty-state
- **AlpineSubmit** -- submit button with Alpine.js attributes
- **BaseFilterFormHelper** -- filter form helper with search field and reset link

### Model mixins (`crispy_crud.models`)
- **AuditOnUpdateOnly** -- suppresses auditlog on creation, only logs updates

### Template fragments (`crispy_crud/fragments/`)
- `common/` -- messages, alerts, page heading
- `table/` -- pagination, table heading/cell, OOB add button
- `details/` -- delete action with confirmation modal, audit history table
- `forms/` -- filter form, field errors, submit/cancel, read-only fields
- `loaders/` -- HTMX loading spinner and busy indicator

### Template tags (`crispy_crud_tags`)
- **filter_form_fields** -- generates HTMX trigger selectors for filter form fields
