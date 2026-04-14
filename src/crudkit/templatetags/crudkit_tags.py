from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def filter_form_fields(context):
    """
    Get keys for all fields in filter form except 'q' field. These are used
    to register change events on the form.

    Returns a comma delimited string of HTMX trigger selectors, e.g.:
    ', change from:[name="field1"], change from:[name="field2"]'
    """
    filter_form = context.get("filter_form", None)
    if filter_form:
        fields = [field for field in filter_form.fields.keys() if field != "q"]
        if fields:
            return mark_safe(", " + ", ".join(["change from:[name='%s']" % field for field in fields]))
    return ""
