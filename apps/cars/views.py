from datetime import timedelta
import calendar

from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.bookings.models import Booking
from apps.bookings.services import suggest_alternative_slots
from apps.cars.forms import CarForm, CarImageUploadForm, CarPricingForm
from apps.cars.models import Car, CarImage
from apps.core.mixins import ManagerRequiredMixin


class CarListView(ListView):
    template_name = "cars/car_list.html"
    model = Car
    context_object_name = "cars"
    paginate_by = 12

    def get_queryset(self):
        qs = Car.objects.select_related("pricing").filter(status=Car.Status.AVAILABLE)
        brand = self.request.GET.get("brand")
        model = self.request.GET.get("model")
        fuel_type = self.request.GET.get("fuel_type")
        seating_capacity = self.request.GET.get("seating_capacity")
        driver_available = self.request.GET.get("driver_available")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        exact_price = self.request.GET.get("price")
        if brand:
            qs = qs.filter(brand__icontains=brand)
        if model:
            qs = qs.filter(model__icontains=model)
        if fuel_type:
            qs = qs.filter(fuel_type=fuel_type)
        if seating_capacity:
            qs = qs.filter(seating_capacity=seating_capacity)
        if driver_available in ["true", "false"]:
            qs = qs.filter(is_driver_available=(driver_available == "true"))
        if exact_price:
            qs = qs.filter(pricing__hourly_rate=exact_price)
        if min_price:
            qs = qs.filter(pricing__hourly_rate__gte=min_price)
        if max_price:
            qs = qs.filter(pricing__hourly_rate__lte=max_price)
        return qs


class CarDetailView(DetailView):
    template_name = "cars/car_detail.html"
    model = Car
    context_object_name = "car"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car = self.object
        context["reviews"] = car.reviews.select_related("customer").order_by("-created_at")[:10]
        context["average_rating"] = car.reviews.aggregate(avg=Avg("rating"))["avg"]
        now = timezone.now()
        range_end = now + timedelta(days=14)
        blocked_bookings = car.bookings.filter(
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED, Booking.Status.ONGOING],
            end_datetime__gt=now,
            start_datetime__lt=range_end,
        ).order_by("start_datetime")
        context["blocked_bookings"] = blocked_bookings

        duration_hours = self.request.GET.get("duration_hours", str(Booking.MIN_BOOKING_HOURS))
        try:
            duration_hours_int = int(duration_hours)
        except (TypeError, ValueError):
            duration_hours_int = Booking.MIN_BOOKING_HOURS
        if duration_hours_int < Booking.MIN_BOOKING_HOURS:
            duration_hours_int = Booking.MIN_BOOKING_HOURS
        if duration_hours_int > 72:
            duration_hours_int = 72
        desired_start = now
        desired_end = desired_start + timedelta(hours=duration_hours_int)
        context["duration_hours"] = duration_hours_int
        context["next_available_slots"] = suggest_alternative_slots(car, desired_start, desired_end, limit=5)
        month_param = self.request.GET.get("month")
        today_local = timezone.localdate()
        if month_param:
            try:
                year_str, month_str = month_param.split("-")
                year = int(year_str)
                month = int(month_str)
                display_date = today_local.replace(year=year, month=month, day=1)
            except (ValueError, TypeError):
                display_date = today_local.replace(day=1)
        else:
            display_date = today_local.replace(day=1)

        cal = calendar.Calendar(firstweekday=0)
        month_weeks = cal.monthdatescalendar(display_date.year, display_date.month)
        month_start = timezone.make_aware(
            timezone.datetime(display_date.year, display_date.month, 1, 0, 0, 0),
            timezone.get_current_timezone(),
        )
        last_day = calendar.monthrange(display_date.year, display_date.month)[1]
        month_end = timezone.make_aware(
            timezone.datetime(display_date.year, display_date.month, last_day, 23, 59, 59),
            timezone.get_current_timezone(),
        )
        month_bookings = car.bookings.filter(
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED, Booking.Status.ONGOING],
            end_datetime__gte=month_start,
            start_datetime__lte=month_end,
        )
        day_meta = {}
        for booking in month_bookings:
            start_date = timezone.localtime(booking.start_datetime).date()
            end_date = timezone.localtime(booking.end_datetime).date()
            cursor = max(start_date, display_date.replace(day=1))
            month_last_date = display_date.replace(day=last_day)
            while cursor <= min(end_date, month_last_date):
                key = cursor.isoformat()
                if key not in day_meta:
                    day_meta[key] = {"has_confirmed": False, "has_pending": False}
                if booking.status in [Booking.Status.CONFIRMED, Booking.Status.ONGOING]:
                    day_meta[key]["has_confirmed"] = True
                elif booking.status == Booking.Status.PENDING:
                    day_meta[key]["has_pending"] = True
                cursor += timedelta(days=1)

        month_grid = []
        for week in month_weeks:
            week_cells = []
            for day in week:
                key = day.isoformat()
                meta = day_meta.get(key, {"has_confirmed": False, "has_pending": False})
                week_cells.append(
                    {
                        "date": day,
                        "in_month": day.month == display_date.month,
                        "is_today": day == today_local,
                        "is_confirmed": meta["has_confirmed"],
                        "is_pending_only": (not meta["has_confirmed"]) and meta["has_pending"],
                    }
                )
            month_grid.append(week_cells)

        prev_month = (display_date.replace(day=1) - timedelta(days=1)).replace(day=1)
        next_month = (display_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        context["calendar_month_label"] = display_date.strftime("%B %Y")
        context["calendar_month_grid"] = month_grid
        context["calendar_prev_month"] = prev_month.strftime("%Y-%m")
        context["calendar_next_month"] = next_month.strftime("%Y-%m")
        return context


class ManagerCarListView(ManagerRequiredMixin, ListView):
    template_name = "cars/manager_car_list.html"
    context_object_name = "cars"
    model = Car


class ManagerCarCreateView(ManagerRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = "cars/manager_car_form.html"
    success_url = reverse_lazy("manager-car-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pricing_form"] = context.get("pricing_form") or CarPricingForm(self.request.POST or None)
        context["image_form"] = context.get("image_form") or CarImageUploadForm(self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pricing_form = context["pricing_form"]
        image_form = context["image_form"]
        if not pricing_form.is_valid() or not image_form.is_valid():
            return self.form_invalid(form)
        self.object = form.save()
        pricing = pricing_form.save(commit=False)
        pricing.car = self.object
        pricing.save()
        for img in image_form.cleaned_data.get("images", []):
            CarImage.objects.create(car=self.object, image=img)
        messages.success(self.request, "Car created.")
        return redirect(self.success_url)


class ManagerCarUpdateView(ManagerRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = "cars/manager_car_form.html"
    success_url = reverse_lazy("manager-car-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pricing_instance = getattr(self.object, "pricing", None)
        context["pricing_form"] = context.get("pricing_form") or CarPricingForm(self.request.POST or None, instance=pricing_instance)
        context["image_form"] = context.get("image_form") or CarImageUploadForm(self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pricing_form = context["pricing_form"]
        image_form = context["image_form"]
        if not pricing_form.is_valid() or not image_form.is_valid():
            return self.form_invalid(form)
        self.object = form.save()
        pricing = pricing_form.save(commit=False)
        pricing.car = self.object
        pricing.save()
        for img in image_form.cleaned_data.get("images", []):
            CarImage.objects.create(car=self.object, image=img)
        messages.success(self.request, "Car updated.")
        return redirect(self.success_url)


class ManagerCarDeleteView(ManagerRequiredMixin, DeleteView):
    model = Car
    success_url = reverse_lazy("manager-car-list")
    template_name = "cars/manager_car_confirm_delete.html"
