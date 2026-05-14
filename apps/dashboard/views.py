from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import TemplateView

from apps.bookings.models import Booking
from apps.cars.models import Car
from apps.core.mixins import ManagerRequiredMixin
from apps.users.models import User


class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = "dashboard/manager_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_bookings"] = Booking.objects.count()
        context["total_cars"] = Car.objects.count()
        context["active_users"] = User.objects.filter(is_active=True).count()
        revenue = Booking.objects.filter(status__in=[Booking.Status.CONFIRMED, Booking.Status.ONGOING, Booking.Status.COMPLETED]).aggregate(
            revenue=Sum("total_amount")
        )
        context["revenue"] = revenue["revenue"] or 0
        context["status_counts"] = Booking.objects.values("status").annotate(total=Count("id")).order_by("status")
        return context


class CustomerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/customer_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_bookings = Booking.objects.filter(customer=self.request.user)
        context["total_bookings"] = user_bookings.count()
        context["active_bookings"] = user_bookings.filter(status__in=[Booking.Status.CONFIRMED, Booking.Status.ONGOING]).count()
        context["completed_bookings"] = user_bookings.filter(status=Booking.Status.COMPLETED).count()
        spend = user_bookings.filter(status__in=[Booking.Status.CONFIRMED, Booking.Status.ONGOING, Booking.Status.COMPLETED]).aggregate(
            total=Sum("total_amount")
        )
        context["total_spend"] = spend["total"] or 0
        context["recent_bookings"] = user_bookings.select_related("car", "driver").order_by("-created_at")[:5]
        return context
