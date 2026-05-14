from django.db import models


class Driver(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        ON_TRIP = "on_trip", "On Trip"
        OFF_DUTY = "off_duty", "Off Duty"

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    driver_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
