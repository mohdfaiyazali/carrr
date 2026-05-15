from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "customer", "booking", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("car__brand", "car__model", "customer__username", "booking__id", "comment")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
