from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import User
from .roles import ensure_role_groups, sync_user_role_group


@receiver(post_migrate)
def create_role_groups(sender, **kwargs):
    if sender.name == "accounts":
        ensure_role_groups()


@receiver(post_save, sender=User)
def update_role_group(sender, instance, raw=False, **kwargs):
    if not raw:
        sync_user_role_group(instance)
