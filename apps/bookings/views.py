from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView

from apps.bookings.forms import BookingCreateForm
from apps.bookings.models import Booking
from apps.cars.models import Car


class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingCreateForm
    template_name = "bookings/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.car = get_object_or_404(Car.objects.select_related("pricing"), pk=kwargs["car_id"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["car"] = self.car
        return kwargs

    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.customer = self.request.user
        booking.car = self.car
        booking.base_amount = form.cleaned_data["base_amount"]
        booking.driver_amount = form.cleaned_data["driver_amount"]
        booking.total_amount = form.cleaned_data["total_amount"]
        booking.save()
        send_mail(
            subject="Booking created",
            message=f"Your booking #{booking.id} was created successfully.",
            from_email="noreply@carz.local",
            recipient_list=[self.request.user.email] if self.request.user.email else [],
            fail_silently=True,
        )
        messages.success(self.request, "Booking created successfully.")
        return redirect("booking-history")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["car"] = self.car
        return context


class BookingHistoryView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_history.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.select_related("car", "driver").filter(customer=self.request.user).order_by("-created_at")
