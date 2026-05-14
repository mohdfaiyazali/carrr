from datetime import timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.bookings.models import Booking
from apps.cars.models import Car, CarPricing
from apps.drivers.models import Driver
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed fake users, cars, drivers, and bookings for testing."

    def add_arguments(self, parser):
        parser.add_argument("--customers", type=int, default=15)
        parser.add_argument("--managers", type=int, default=2)
        parser.add_argument("--drivers", type=int, default=10)
        parser.add_argument("--cars", type=int, default=20)
        parser.add_argument("--bookings", type=int, default=40)
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        fake = Faker()

        if options["clear"]:
            Booking.objects.all().delete()
            CarPricing.objects.all().delete()
            Car.objects.all().delete()
            Driver.objects.all().delete()
            User.objects.exclude(is_superuser=True).delete()

        managers = []
        for i in range(options["managers"]):
            managers.append(
                User.objects.create_user(
                    username=f"manager{i+1}",
                    email=f"manager{i+1}@test.com",
                    password="Pass@12345",
                    role=User.Role.MANAGER,
                    phone=fake.phone_number()[:20],
                )
            )

        customers = []
        for i in range(options["customers"]):
            customers.append(
                User.objects.create_user(
                    username=f"customer{i+1}",
                    email=f"customer{i+1}@test.com",
                    password="Pass@12345",
                    role=User.Role.CUSTOMER,
                    phone=fake.phone_number()[:20],
                )
            )

        drivers = []
        for i in range(options["drivers"]):
            drivers.append(
                Driver.objects.create(
                    name=fake.name(),
                    phone=fake.phone_number()[:20],
                    license_number=f"LIC-{10000+i}",
                    experience_years=random.randint(1, 15),
                    status=random.choice([Driver.Status.AVAILABLE, Driver.Status.OFF_DUTY]),
                    driver_hourly_rate=Decimal(random.randint(100, 400)),
                    is_active=True,
                )
            )

        cars = []
        brands = ["Toyota", "Honda", "Hyundai", "Maruti", "Kia", "Tata"]
        models = ["City", "Creta", "Baleno", "Seltos", "Nexon", "Innova"]
        for _ in range(options["cars"]):
            car = Car.objects.create(
                brand=random.choice(brands),
                model=random.choice(models),
                year=random.randint(2016, 2025),
                color=random.choice(["White", "Black", "Blue", "Silver", "Red"]),
                fuel_type=random.choice([c[0] for c in Car.FuelType.choices]),
                transmission=random.choice([c[0] for c in Car.Transmission.choices]),
                seating_capacity=random.choice([4, 5, 7]),
                description=fake.sentence(),
                is_driver_available=random.choice([True, False]),
                status=Car.Status.AVAILABLE,
            )
            CarPricing.objects.create(
                car=car,
                hourly_rate=Decimal(random.randint(200, 1000)),
                half_day_rate=Decimal(random.randint(1200, 3500)),
                full_day_rate=Decimal(random.randint(2200, 6500)),
                per_day_rate=Decimal(random.randint(2000, 6000)),
            )
            cars.append(car)

        statuses = [s[0] for s in Booking.Status.choices]
        for _ in range(options["bookings"]):
            car = random.choice(cars)
            customer = random.choice(customers)
            start = timezone.now() + timedelta(days=random.randint(-3, 10), hours=random.randint(0, 23))
            duration_hours = random.randint(2, 72)
            end = start + timedelta(hours=duration_hours)
            booking_type = random.choice([Booking.BookingType.SELF_DRIVE, Booking.BookingType.WITH_DRIVER])
            driver = random.choice(drivers) if booking_type == Booking.BookingType.WITH_DRIVER else None
            base_amount = car.pricing.hourly_rate * Decimal(duration_hours)
            driver_amount = (driver.driver_hourly_rate * Decimal(duration_hours)) if driver else Decimal("0")
            Booking.objects.create(
                customer=customer,
                car=car,
                driver=driver,
                start_datetime=start,
                end_datetime=end,
                booking_type=booking_type,
                status=random.choice(statuses),
                base_amount=base_amount,
                driver_amount=driver_amount,
                total_amount=base_amount + driver_amount,
            )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
