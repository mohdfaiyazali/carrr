from django.contrib import admin

from apps.drivers.models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "license_number", "experience_years", "status", "driver_hourly_rate", "is_active")
    list_filter = ("status", "is_active", "experience_years")
    search_fields = ("name", "phone", "license_number")
    ordering = ("name",)
