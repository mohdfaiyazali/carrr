from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.cars.models import Car
from apps.drivers.models import Driver


class Booking(models.Model):
    MIN_BOOKING_HOURS = 6
    class BookingType(models.TextChoices):
        SELF_DRIVE = "self_drive", "Self Drive"
        WITH_DRIVER = "with_driver", "With Driver"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
    class PaymentStatus(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"
        PAID = "paid", "Paid"
        REFUND_PENDING = "refund_pending", "Refund Pending"
        REFUNDED = "refunded", "Refunded"

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
    advance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("End datetime must be after start datetime.")
        duration = self.end_datetime - self.start_datetime
        min_duration = timedelta(hours=self.MIN_BOOKING_HOURS)
        if duration < min_duration:
            raise ValidationError(f"Minimum booking duration is {self.MIN_BOOKING_HOURS} hours.")
        if self.booking_type == self.BookingType.WITH_DRIVER and not self.driver:
            raise ValidationError("Driver is required for with-driver bookings.")

    def __str__(self):
        return f"Booking #{self.pk} - {self.customer}"


class BookingPayment(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        CAPTURED = "captured", "Captured"
        REFUND_PENDING = "refund_pending", "Refund Pending"
        REFUNDED = "refunded", "Refunded"
        FAILED = "failed", "Failed"

    booking = models.OneToOneField(Booking, related_name="payment", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, default="razorpay")
    razorpay_order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED, db_index=True)
    refund_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
