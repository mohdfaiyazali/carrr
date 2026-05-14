from decimal import Decimal

from django import forms
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import calculate_car_charge, calculate_duration_hours, has_booking_overlap
from apps.drivers.models import Driver


class BookingCreateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["start_datetime", "end_datetime", "booking_type", "driver"]
        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "booking_type": forms.Select(attrs={"class": "form-select"}),
            "driver": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop("car")
        super().__init__(*args, **kwargs)
        self.fields["driver"].queryset = Driver.objects.filter(status=Driver.Status.AVAILABLE, is_active=True)
        self.fields["driver"].required = False

    def clean(self):
        cleaned = super().clean()
        start_dt = cleaned.get("start_datetime")
        end_dt = cleaned.get("end_datetime")
        booking_type = cleaned.get("booking_type")
        driver = cleaned.get("driver")
        if not start_dt or not end_dt:
            return cleaned
        if start_dt < timezone.now():
            raise forms.ValidationError("Start datetime must be in the future.")
        if end_dt <= start_dt:
            raise forms.ValidationError("End datetime must be after start datetime.")
        if booking_type == Booking.BookingType.WITH_DRIVER and not driver:
            raise forms.ValidationError("Please choose a driver.")
        if has_booking_overlap(self.car, start_dt, end_dt):
            raise forms.ValidationError("This car is already booked for the selected slot.")

        duration_hours = calculate_duration_hours(start_dt, end_dt)
        base_amount = calculate_car_charge(self.car.pricing, duration_hours)
        driver_amount = Decimal("0")
        if booking_type == Booking.BookingType.WITH_DRIVER and driver:
            driver_amount = driver.driver_hourly_rate * duration_hours
        cleaned["base_amount"] = base_amount
        cleaned["driver_amount"] = driver_amount
        cleaned["total_amount"] = base_amount + driver_amount
        return cleaned
