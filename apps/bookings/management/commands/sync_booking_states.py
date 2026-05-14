from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.status_services import apply_booking_state


class Command(BaseCommand):
    help = "Auto-complete overdue confirmed/ongoing bookings and release car/driver."

    def handle(self, *args, **options):
        now = timezone.now()
        bookings = Booking.objects.filter(
            status__in=[Booking.Status.CONFIRMED, Booking.Status.ONGOING],
            end_datetime__lt=now,
        ).select_related("car", "driver")
        count = 0
        for booking in bookings:
            apply_booking_state(booking, Booking.Status.COMPLETED)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Completed {count} overdue booking(s)."))
