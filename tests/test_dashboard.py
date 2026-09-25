import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_dashboard_requires_login(client):
    response = client.get(reverse("chem_core:dashboard"))
    assert response.status_code == 302


@pytest.mark.parametrize(
    ("role", "visible", "hidden"),
    [
        ("student", "Safety resources", "Inventory attention"),
        ("faculty", "Inventory attention", "System management"),
        ("admin", "System management", None),
    ],
)
def test_dashboard_is_role_aware(client, django_user_model, role, visible, hidden):
    user = django_user_model.objects.create_user(username=role, password="test", role=role)
    client.force_login(user)
    response = client.get(reverse("chem_core:dashboard"))
    assert response.status_code == 200
    content = response.content.decode()
    assert visible in content
    if hidden:
        assert hidden not in content
