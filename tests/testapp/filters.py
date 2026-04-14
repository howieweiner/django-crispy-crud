import django_filters

from .models import Widget


class WidgetFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Widget
        fields = ["q", "is_active"]
