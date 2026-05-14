from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.cars.models import Car
from apps.drivers.models import Driver


class Booking(models.Model):
    class BookingType(models.TextChoices):
        SELF_DRIVE = "self_drive", "Self Drive"
        WITH_DRIVER = "with_driver", "With Driver"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bookings", on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name="bookings", on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, related_name="bookings", on_delete=models.SET_NULL, blank=True, null=True)
    start_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField(db_index=True)
    booking_type = models.CharField(max_length=20, choices=BookingType.choices, default=BookingType.SELF_DRIVE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    base_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    driver_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be after start datetime.")
        if self.booking_type == self.BookingType.WITH_DRIVER and not self.driver:
            raise ValidationError("Driver is required for with-driver bookings.")

    def __str__(self):
        return f"Booking #{self.pk} - {self.customer}"
