from datetime import timedelta
from decimal import Decimal

from apps.bookings.models import Booking


def has_booking_overlap(car, start_dt, end_dt, exclude_booking_id=None):
    qs = Booking.objects.filter(
        car=car,
        status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED, Booking.Status.ONGOING],
        start_datetime__lt=end_dt,
        end_datetime__gt=start_dt,
    )
    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)
    return qs.exists()


def calculate_duration_hours(start_dt, end_dt):
    delta: timedelta = end_dt - start_dt
    return Decimal(delta.total_seconds()) / Decimal("3600")


def calculate_car_charge(pricing, duration_hours):
    if duration_hours <= 12:
        return pricing.hourly_rate * duration_hours
    if duration_hours <= 24:
        return pricing.full_day_rate
    days = int(duration_hours // 24)
    remaining_hours = duration_hours - (days * 24)
    return (pricing.per_day_rate * days) + (pricing.hourly_rate * remaining_hours)
