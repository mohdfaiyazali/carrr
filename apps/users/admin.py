from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "email", "first_name", "last_name", "role", "phone", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("id",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Car Rental", {"fields": ("role", "phone")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Car Rental", {"fields": ("role", "phone")}),
    )
