from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class WuChemUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("WuChem access", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("WuChem access", {"fields": ("role",)}),)
    list_display = (*UserAdmin.list_display, "role")
    list_filter = (*UserAdmin.list_filter, "role")
