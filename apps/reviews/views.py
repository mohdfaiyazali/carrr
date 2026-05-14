from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.bookings.models import Booking
from apps.reviews.forms import ReviewCreateForm
from apps.reviews.models import Review


@login_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status != Booking.Status.COMPLETED:
        messages.error(request, "You can review only completed bookings.")
        return redirect("booking-history")
    if hasattr(booking, "review"):
        messages.error(request, "Review already submitted for this booking.")
        return redirect("booking-history")

    if request.method == "POST":
        form = ReviewCreateForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.car = booking.car
            review.customer = request.user
            review.save()
            messages.success(request, "Review submitted.")
            return redirect("car-detail", pk=booking.car_id)
    else:
        form = ReviewCreateForm()
    return render(request, "reviews/review_form.html", {"form": form, "booking": booking})
