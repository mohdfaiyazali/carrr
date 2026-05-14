from django.urls import path

from apps.bookings.views import (
    BookingCreateView,
    BookingHistoryView,
    ManagerBookingApproveView,
    ManagerBookingListView,
    manager_booking_complete,
    manager_booking_reject,
)

urlpatterns = [
    path("new/<int:car_id>/", BookingCreateView.as_view(), name="booking-create"),
    path("my/", BookingHistoryView.as_view(), name="booking-history"),
    path("manager/bookings/", ManagerBookingListView.as_view(), name="manager-booking-list"),
    path("manager/bookings/<int:booking_id>/approve/", ManagerBookingApproveView.as_view(), name="manager-booking-approve"),
    path("manager/bookings/<int:booking_id>/reject/", manager_booking_reject, name="manager-booking-reject"),
    path("manager/bookings/<int:booking_id>/complete/", manager_booking_complete, name="manager-booking-complete"),
]
