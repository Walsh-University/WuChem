from unittest.mock import Mock

import pytest
from django.test import RequestFactory
from django.urls import reverse

from chem_core import status, views

pytestmark = pytest.mark.django_db


def test_check_database_reports_success(monkeypatch):
    cursor = Mock()
    connection = Mock()
    connection.cursor.return_value.__enter__ = Mock(return_value=cursor)
    connection.cursor.return_value.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(status, "connections", {"default": connection})

    assert status.check_database() == {"name": "database", "ok": True}
    cursor.execute.assert_called_once_with("SELECT 1;")
    cursor.fetchone.assert_called_once_with()


def test_check_database_reports_operational_error(monkeypatch):
    connection = Mock()
    connection.cursor.side_effect = status.OperationalError("database unavailable")
    monkeypatch.setattr(status, "connections", {"default": connection})

    result = status.check_database()

    assert result["name"] == "database"
    assert result["ok"] is False
    assert "database unavailable" in result["detail"]


def test_get_system_status_includes_database_details_when_internal(monkeypatch):
    monkeypatch.setattr(status, "check_database", lambda: {"name": "database", "ok": True})

    public_status = status.get_system_status()
    internal_status = status.get_system_status(include_internal=True)

    assert public_status["status"] == "Operational"
    assert "dependencies" not in public_status
    assert internal_status["dependencies"] == [{"name": "database", "ok": True}]
    assert internal_status["last_checked"]


def test_get_system_status_reports_database_down(monkeypatch):
    monkeypatch.setattr(
        status,
        "check_database",
        lambda: {"name": "database", "ok": False, "detail": "unavailable"},
    )

    assert status.get_system_status()["status"] == "Down"


def test_home_renders_for_authenticated_user(django_user_model):
    user = django_user_model.objects.create_user(username="home-user", password="test-password")
    request = RequestFactory().get("/")
    request.user = user

    response = views.home(request)

    assert response.status_code == 200
    assert b"WuChem" in response.content


def test_status_endpoints_require_login(client):
    assert client.get(reverse("chem_core:status_public")).status_code == 302
    assert client.get(reverse("chem_core:status_internal")).status_code == 302


def test_status_public_endpoint_hides_dependency_details(client, django_user_model, monkeypatch):
    user = django_user_model.objects.create_user(username="public-status", password="test-password")
    client.force_login(user)
    monkeypatch.setattr(views, "get_system_status", lambda include_internal: {"status": "Operational"})

    response = client.get(reverse("chem_core:status_public"))

    assert response.status_code == 200
    assert response.json() == {"status": "Operational"}


def test_internal_status_requires_staff(client, django_user_model):
    user = django_user_model.objects.create_user(username="non-staff", password="test-password")
    client.force_login(user)

    response = client.get(reverse("chem_core:status_internal"))

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_internal_status_returns_dependencies_for_staff(client, django_user_model, monkeypatch):
    user = django_user_model.objects.create_user(username="staff", password="test-password", role="admin")
    client.force_login(user)
    payload = {"status": "Operational", "dependencies": [{"name": "database", "ok": True}]}
    monkeypatch.setattr(views, "get_system_status", lambda include_internal: payload)

    response = client.get(reverse("chem_core:status_internal"))

    assert response.status_code == 200
    assert response.json() == payload
