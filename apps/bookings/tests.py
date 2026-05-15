from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.bookings.models import Booking
from apps.bookings.services import has_booking_overlap
from apps.cars.models import Car, CarPricing
from apps.users.models import User


class BookingFlowTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="cust1", password="Pass@12345", role=User.Role.CUSTOMER)
        self.manager = User.objects.create_user(username="mgr1", password="Pass@12345", role=User.Role.MANAGER)
        self.car = Car.objects.create(
            brand="Toyota",
            model="City",
            year=2022,
            color="White",
            fuel_type=Car.FuelType.PETROL,
            transmission=Car.Transmission.MANUAL,
            seating_capacity=5,
            status=Car.Status.AVAILABLE,
        )
        CarPricing.objects.create(car=self.car, hourly_rate=Decimal("500"), half_day_rate=Decimal("2500"), full_day_rate=Decimal("4000"), per_day_rate=Decimal("3500"))

    def test_booking_overlap_service(self):
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=4)
        Booking.objects.create(customer=self.customer, car=self.car, start_datetime=start, end_datetime=end, total_amount=1000)
        self.assertTrue(has_booking_overlap(self.car, start + timedelta(hours=1), end + timedelta(hours=1)))

    def test_customer_can_create_booking(self):
        self.client.login(username="cust1", password="Pass@12345")
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=6)
        resp = self.client.post(reverse("booking-create", kwargs={"car_id": self.car.id}), {
            "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
            "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
            "booking_type": Booking.BookingType.SELF_DRIVE,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Booking.objects.count(), 1)

    def test_customer_cannot_create_booking_less_than_6_hours(self):
        self.client.login(username="cust1", password="Pass@12345")
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(hours=5)
        resp = self.client.post(reverse("booking-create", kwargs={"car_id": self.car.id}), {
            "start_datetime": start.strftime("%Y-%m-%dT%H:%M"),
            "end_datetime": end.strftime("%Y-%m-%dT%H:%M"),
            "booking_type": Booking.BookingType.SELF_DRIVE,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Minimum booking duration is 6 hours.")
        self.assertEqual(Booking.objects.count(), 0)

    def test_manager_can_mark_ongoing(self):
        booking = Booking.objects.create(
            customer=self.customer,
            car=self.car,
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=6),
            status=Booking.Status.CONFIRMED,
            total_amount=1000,
        )
        self.client.login(username="mgr1", password="Pass@12345")
        resp = self.client.get(reverse("manager-booking-start", kwargs={"booking_id": booking.id}))
        booking.refresh_from_db()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(booking.status, Booking.Status.ONGOING)
