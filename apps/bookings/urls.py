from django.urls import path

from apps.bookings.views import BookingCreateView, BookingHistoryView

urlpatterns = [
    path("new/<int:car_id>/", BookingCreateView.as_view(), name="booking-create"),
    path("my/", BookingHistoryView.as_view(), name="booking-history"),
]
