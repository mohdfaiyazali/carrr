from datetime import timedelta
from decimal import Decimal

from django.db.models import Q

from apps.bookings.models import Booking
from apps.cars.models import Car


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


def has_driver_overlap(driver, start_dt, end_dt, exclude_booking_id=None):
    qs = Booking.objects.filter(
        driver=driver,
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


def suggest_alternative_slots(car, start_dt, end_dt, limit=3):
    duration = end_dt - start_dt
    suggestions = []
    probe_start = end_dt
    for _ in range(30):
        probe_end = probe_start + duration
        if not has_booking_overlap(car, probe_start, probe_end):
            suggestions.append((probe_start, probe_end))
            if len(suggestions) >= limit:
                break
        probe_start = probe_start + timedelta(hours=1)
    return suggestions


def suggest_similar_available_cars(car, start_dt, end_dt, limit=4):
    base_qs = Car.objects.filter(status=Car.Status.AVAILABLE).exclude(id=car.id)
    ordered = base_qs.filter(
        Q(brand__iexact=car.brand) | Q(fuel_type=car.fuel_type) | Q(seating_capacity=car.seating_capacity)
    ).order_by("brand", "model")
    suggestions = []
    for candidate in ordered:
        if not has_booking_overlap(candidate, start_dt, end_dt):
            suggestions.append(candidate)
            if len(suggestions) >= limit:
                return suggestions
    for candidate in base_qs.order_by("brand", "model"):
        if candidate in suggestions:
            continue
        if not has_booking_overlap(candidate, start_dt, end_dt):
            suggestions.append(candidate)
            if len(suggestions) >= limit:
                break
    return suggestions
