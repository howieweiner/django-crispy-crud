# Changelog

## v1.0.0 (2026-07-03)

First public release on PyPI, published as `django-crispy-crud` (import as `crispy_crud`).

### Features

- CRUD view mixins for Django with HTMX-driven filtering, pagination, and forms
- Crispy form helpers with Alpine.js dirty-state submit and cancel handling
- Reusable template fragments: tables, forms, loaders, alerts, and audit history
- Optional audit log support via `django-auditlog` (`[audit]` extra)
- Alpine.js/HTMX static assets for form-state tracking and pagination

### Fixes

- Escape the cancel link URL and same-site-validate the referrer to prevent reflected XSS

## v0.1.0

### Features

- Initial (unpublished) release
- CRUD views, forms, and template fragments for Django with HTMX, Alpine.js, and Tailwind CSS
- Optional audit log support via `django-auditlog` (`[audit]` extra)
