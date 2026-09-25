import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    ("role", "inventory", "system"),
    [("student", False, False), ("faculty", True, False), ("admin", True, True)],
)
def test_role_capabilities(role, inventory, system):
    user = get_user_model().objects.create_user(username=role, role=role)
    assert user.can_manage_inventory is inventory
    assert user.can_manage_system is system
    assert user.groups.filter(name=user.get_role_display()).exists()


def test_admin_role_can_access_django_admin():
    user = get_user_model().objects.create_user(username="admin", role="admin")
    assert user.is_staff is True
    assert user.has_perm("accounts.change_user") is True


def test_changing_admin_to_faculty_removes_admin_access():
    user = get_user_model().objects.create_user(username="role-change", role="admin")
    user.role = get_user_model().Role.FACULTY
    user.save()
    assert user.is_staff is False
    assert user.groups.filter(name="Faculty").exists()
    assert not user.groups.filter(name="Admin").exists()
