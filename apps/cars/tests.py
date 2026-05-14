from django.test import TestCase
from decimal import Decimal

from apps.cars.models import Car, CarPricing


class CarFilterTests(TestCase):
    def setUp(self):
        car1 = Car.objects.create(
            brand="Honda", model="City", year=2022, color="Red", fuel_type=Car.FuelType.PETROL,
            transmission=Car.Transmission.MANUAL, seating_capacity=5, is_driver_available=True
        )
        CarPricing.objects.create(car=car1, hourly_rate=Decimal("500"), half_day_rate=2000, full_day_rate=3500, per_day_rate=3000)
        car2 = Car.objects.create(
            brand="Toyota", model="Innova", year=2021, color="White", fuel_type=Car.FuelType.DIESEL,
            transmission=Car.Transmission.AUTOMATIC, seating_capacity=7, is_driver_available=False
        )
        CarPricing.objects.create(car=car2, hourly_rate=Decimal("900"), half_day_rate=3000, full_day_rate=5000, per_day_rate=4500)

    def test_car_list_filter_by_seating(self):
        resp = self.client.get("/cars/?seating_capacity=7")
        self.assertContains(resp, "Innova")
        self.assertNotContains(resp, "City")
