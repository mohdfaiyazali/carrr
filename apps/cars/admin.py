from django.contrib import admin

from apps.cars.models import Car, CarImage, CarPricing


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


class CarPricingInline(admin.StackedInline):
    model = CarPricing
    extra = 0
    max_num = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "brand", "model", "year", "fuel_type", "transmission", "seating_capacity", "status", "is_driver_available")
    list_filter = ("brand", "fuel_type", "transmission", "seating_capacity", "status", "is_driver_available")
    search_fields = ("brand", "model", "color", "description")
    ordering = ("-id",)
    inlines = [CarPricingInline, CarImageInline]


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "image")
    list_filter = ("car__brand",)
    search_fields = ("car__brand", "car__model")
    ordering = ("-id",)


@admin.register(CarPricing)
class CarPricingAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "hourly_rate", "half_day_rate", "full_day_rate", "per_day_rate")
    search_fields = ("car__brand", "car__model")
    ordering = ("-id",)
