from django.db import models

from apps.bookings.models import Booking
from apps.cars.models import Car


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="reviews")
    customer = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gte=1) & models.Q(rating__lte=5), name="rating_between_1_5"),
        ]

    def __str__(self):
        return f"Review {self.rating}/5 for {self.car}"
