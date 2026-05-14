from django.test import TestCase
from datetime import timedelta

from django.utils import timezone

from apps.bookings.models import Booking
from apps.cars.models import Car, CarPricing
from apps.reviews.models import Review
from apps.users.models import User


class ReviewTests(TestCase):
    def test_review_created_for_completed_booking(self):
        user = User.objects.create_user(username="custx", password="Pass@12345", role=User.Role.CUSTOMER)
        car = Car.objects.create(
            brand="Kia", model="Seltos", year=2022, color="Black",
            fuel_type=Car.FuelType.PETROL, transmission=Car.Transmission.MANUAL, seating_capacity=5
        )
        CarPricing.objects.create(car=car, hourly_rate=500, half_day_rate=2000, full_day_rate=3500, per_day_rate=3000)
        booking = Booking.objects.create(
            customer=user,
            car=car,
            start_datetime=timezone.now() - timedelta(days=2),
            end_datetime=timezone.now() - timedelta(days=1),
            status=Booking.Status.COMPLETED,
            total_amount=3000,
        )
        Review.objects.create(booking=booking, car=car, customer=user, rating=5, comment="Great")
        self.assertEqual(Review.objects.count(), 1)
