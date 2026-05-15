from django.contrib import admin

from apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "car",
        "driver",
        "booking_type",
        "status",
        "start_datetime",
        "end_datetime",
        "total_amount",
    )
    list_filter = ("booking_type", "status", "start_datetime", "end_datetime")
    search_fields = ("customer__username", "customer__email", "car__brand", "car__model", "driver__name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
