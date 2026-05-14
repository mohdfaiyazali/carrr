from django.db import models


class Car(models.Model):
    class FuelType(models.TextChoices):
        PETROL = "petrol", "Petrol"
        DIESEL = "diesel", "Diesel"
        CNG = "cng", "CNG"
        ELECTRIC = "electric", "Electric"

    class Transmission(models.TextChoices):
        MANUAL = "manual", "Manual"
        AUTOMATIC = "automatic", "Automatic"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        UNDER_SERVICE = "under_service", "Under Service"
        NOT_AVAILABLE = "not_available", "Not Available"

    brand = models.CharField(max_length=100, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, db_index=True)
    transmission = models.CharField(max_length=20, choices=Transmission.choices)
    seating_capacity = models.PositiveSmallIntegerField(db_index=True)
    description = models.TextField(blank=True)
    is_driver_available = models.BooleanField(default=False, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"


class CarImage(models.Model):
    car = models.ForeignKey(Car, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cars/")


class CarPricing(models.Model):
    car = models.OneToOneField(Car, related_name="pricing", on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    half_day_rate = models.DecimalField(max_digits=10, decimal_places=2)
    full_day_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_day_rate = models.DecimalField(max_digits=10, decimal_places=2)
