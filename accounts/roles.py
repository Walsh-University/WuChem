from django.contrib.auth.models import Group, Permission

from .models import User

ROLE_GROUP_NAMES = {
    User.Role.STUDENT: "Student",
    User.Role.FACULTY: "Faculty",
    User.Role.ADMIN: "Admin",
}


def ensure_role_groups():
    groups = {role: Group.objects.get_or_create(name=group_name)[0] for role, group_name in ROLE_GROUP_NAMES.items()}
    admin_permissions = Permission.objects.filter(content_type__app_label__in={"accounts", "auth"})
    groups[User.Role.ADMIN].permissions.set(admin_permissions)
    return groups


def sync_user_role_group(user):
    """Keep the user's primary role and reserved Django group in sync."""
    role_groups = ensure_role_groups()
    user.groups.remove(*role_groups.values())
    user.groups.add(role_groups[user.role])
