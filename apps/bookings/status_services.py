from apps.bookings.models import Booking
from apps.cars.models import Car
from apps.drivers.models import Driver


def apply_booking_state(booking: Booking, new_status: str):
    booking.status = new_status
    booking.save(update_fields=["status"])

    if new_status in [Booking.Status.CONFIRMED, Booking.Status.ONGOING]:
        booking.car.status = Car.Status.BOOKED
        booking.car.save(update_fields=["status"])
        if booking.driver:
            booking.driver.status = Driver.Status.ON_TRIP
            booking.driver.save(update_fields=["status"])
        return

    if new_status in [Booking.Status.COMPLETED, Booking.Status.CANCELLED]:
        booking.car.status = Car.Status.AVAILABLE
        booking.car.save(update_fields=["status"])
        if booking.driver:
            booking.driver.status = Driver.Status.AVAILABLE
            booking.driver.save(update_fields=["status"])
