from django.urls import path

from apps.reviews.views import create_review

urlpatterns = [
    path("bookings/<int:booking_id>/review/", create_review, name="review-create"),
]
