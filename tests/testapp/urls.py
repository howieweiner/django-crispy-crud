from django.urls import path

from .views import WidgetCreateView, WidgetDeleteView, WidgetListView, WidgetUpdateView

urlpatterns = [
    path("widgets/", WidgetListView.as_view(), name="widget-list"),
    path("widgets/create/", WidgetCreateView.as_view(), name="widget-create"),
    path("widgets/<int:pk>/", WidgetUpdateView.as_view(), name="widget-update"),
    path("widgets/<int:pk>/delete/", WidgetDeleteView.as_view(), name="widget-delete"),
]
