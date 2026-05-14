from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView, UpdateView

from apps.bookings.forms import BookingCreateForm
from apps.bookings.manager_forms import BookingApprovalForm
from apps.bookings.models import Booking
from apps.bookings.services import has_driver_overlap
from apps.bookings.status_services import apply_booking_state
from apps.cars.models import Car
from apps.core.mixins import ManagerRequiredMixin
from apps.users.models import User


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
        form = context.get("form")
        context["alternative_slots"] = getattr(form, "alternative_slots", [])
        context["similar_available_cars"] = getattr(form, "similar_available_cars", [])
        return context


class BookingHistoryView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/booking_history.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.select_related("car", "driver").filter(customer=self.request.user).order_by("-created_at")


class ManagerBookingListView(ManagerRequiredMixin, ListView):
    model = Booking
    template_name = "bookings/manager_booking_list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.select_related("customer", "car", "driver").order_by("-created_at")


def _manager_update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    apply_booking_state(booking, status)
    messages.success(request, f"Booking #{booking.id} updated to {status}.")
    return redirect("manager-booking-list")


def _is_manager(user):
    return user.is_authenticated and (user.role in [User.Role.MANAGER, User.Role.ADMIN] or user.is_superuser)


@login_required
@user_passes_test(_is_manager)
def manager_booking_approve(request, booking_id):
    return _manager_update_booking_status(request, booking_id, Booking.Status.CONFIRMED)


@login_required
@user_passes_test(_is_manager)
def manager_booking_reject(request, booking_id):
    return _manager_update_booking_status(request, booking_id, Booking.Status.CANCELLED)


@login_required
@user_passes_test(_is_manager)
def manager_booking_complete(request, booking_id):
    return _manager_update_booking_status(request, booking_id, Booking.Status.COMPLETED)


@login_required
@user_passes_test(_is_manager)
def manager_booking_start(request, booking_id):
    return _manager_update_booking_status(request, booking_id, Booking.Status.ONGOING)


@login_required
def customer_booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status in [Booking.Status.COMPLETED, Booking.Status.CANCELLED]:
        messages.error(request, "This booking cannot be cancelled.")
        return redirect("booking-history")
    apply_booking_state(booking, Booking.Status.CANCELLED)
    send_mail(
        subject="Booking cancelled",
        message=f"Your booking #{booking.id} has been cancelled.",
        from_email="noreply@carz.local",
        recipient_list=[request.user.email] if request.user.email else [],
        fail_silently=True,
    )
    messages.success(request, f"Booking #{booking.id} cancelled.")
    return redirect("booking-history")


class ManagerBookingApproveView(ManagerRequiredMixin, UpdateView):
    model = Booking
    form_class = BookingApprovalForm
    pk_url_kwarg = "booking_id"
    template_name = "bookings/manager_booking_approve.html"
    success_url = "/bookings/manager/bookings/"

    def form_valid(self, form):
        booking = form.save(commit=False)
        if booking.booking_type == Booking.BookingType.WITH_DRIVER and not booking.driver:
            form.add_error("driver", "Driver is required for with-driver booking.")
            return self.form_invalid(form)
        if booking.driver and has_driver_overlap(booking.driver, booking.start_datetime, booking.end_datetime, exclude_booking_id=booking.id):
            form.add_error("driver", "Selected driver is already assigned in this time slot.")
            return self.form_invalid(form)
        booking.save(update_fields=["driver"])
        apply_booking_state(booking, Booking.Status.CONFIRMED)
        messages.success(self.request, f"Booking #{booking.id} approved.")
        return redirect("manager-booking-list")
