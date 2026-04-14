import pytest
from django.test import Client

from tests.testapp.models import Widget, Gadget


pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def widget():
    return Widget.objects.create(name="Test Widget", description="A test widget")


@pytest.fixture
def widgets():
    return [Widget.objects.create(name=f"Widget {i}") for i in range(30)]


@pytest.fixture
def widget_with_gadget(widget):
    Gadget.objects.create(widget=widget, name="Test Gadget")
    return widget


class TestListView:
    def test_list_renders(self, client):
        response = client.get("/widgets/")
        assert response.status_code == 200
        assert "widgets" in response.content.decode()

    def test_list_shows_widgets(self, client, widget):
        response = client.get("/widgets/")
        assert widget.name in response.content.decode()

    def test_list_has_create_action(self, client):
        response = client.get("/widgets/")
        assert "/widgets/create/" in response.content.decode()

    def test_list_pagination(self, client, widgets):
        response = client.get("/widgets/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Showing" in content

    def test_list_htmx_returns_partial(self, client, widget):
        response = client.get("/widgets/", HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        content = response.content.decode()
        # Partial should not include base template elements
        assert "<!DOCTYPE" not in content
        # Should include table content
        assert widget.name in content

    def test_list_htmx_pushes_url(self, client):
        response = client.get("/widgets/", HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        assert "HX-Push-Url" in response

    def test_list_filter_by_name(self, client):
        Widget.objects.create(name="Alpha")
        Widget.objects.create(name="Beta")
        response = client.get("/widgets/", {"q": "Alpha"})
        content = response.content.decode()
        assert "Alpha" in content
        assert "Beta" not in content

    def test_list_page_size_cookie(self, client, widgets):
        response = client.get("/widgets/", {"paginate_by": "10"})
        assert response.status_code == 200
        assert "paginate_by" in response.cookies

    def test_page_size_options_in_context(self, client):
        response = client.get("/widgets/")
        assert response.context["page_size_options"] == [10, 25, 50, 100]

    def test_filter_form_in_context(self, client):
        response = client.get("/widgets/")
        assert "filter_form" in response.context
        assert "filter_fields" in response.context


class TestCreateView:
    def test_create_form_renders(self, client):
        response = client.get("/widgets/create/")
        assert response.status_code == 200
        assert "Add" in response.content.decode()

    def test_create_saves_record(self, client):
        response = client.post("/widgets/create/", {"name": "New Widget", "description": "Desc", "is_active": True})
        assert response.status_code == 302
        assert Widget.objects.filter(name="New Widget").exists()

    def test_create_heading(self, client):
        response = client.get("/widgets/create/")
        assert response.context["heading"] == "Add widget"


class TestUpdateView:
    def test_update_form_renders(self, client, widget):
        response = client.get(f"/widgets/{widget.pk}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert widget.name in content

    def test_update_saves_changes(self, client, widget):
        response = client.post(
            f"/widgets/{widget.pk}/",
            {"name": "Updated Widget", "description": "Updated", "is_active": True},
        )
        assert response.status_code == 302
        widget.refresh_from_db()
        assert widget.name == "Updated Widget"

    def test_update_heading(self, client, widget):
        response = client.get(f"/widgets/{widget.pk}/")
        assert response.context["heading"] == "Update widget"

    def test_update_has_delete_action(self, client, widget):
        response = client.get(f"/widgets/{widget.pk}/")
        assert response.context["delete_action"] == f"/widgets/{widget.pk}/delete/"

    def test_can_delete_no_related(self, client, widget):
        response = client.get(f"/widgets/{widget.pk}/")
        assert response.context["can_delete"] is True

    def test_cannot_delete_has_related(self, client, widget_with_gadget):
        response = client.get(f"/widgets/{widget_with_gadget.pk}/")
        assert response.context["can_delete"] is False

    def test_success_url_preserves_query_params(self, client, widget):
        response = client.post(
            f"/widgets/{widget.pk}/?is_active=true",
            {"name": "Updated", "description": "d", "is_active": True},
        )
        assert response.status_code == 302
        assert "is_active=true" in response.url


class TestDeleteView:
    def test_delete_confirmation_renders(self, client, widget):
        response = client.get(f"/widgets/{widget.pk}/delete/")
        assert response.status_code == 200
        assert "Delete" in response.content.decode()

    def test_delete_removes_record(self, client, widget):
        response = client.post(f"/widgets/{widget.pk}/delete/")
        assert response.status_code == 302
        assert not Widget.objects.filter(pk=widget.pk).exists()

    def test_delete_protected_record(self, client, widget_with_gadget):
        """Attempting to delete a widget with related gadgets should raise ProtectedError."""
        with pytest.raises(Exception):
            client.post(f"/widgets/{widget_with_gadget.pk}/delete/")
        assert Widget.objects.filter(pk=widget_with_gadget.pk).exists()
