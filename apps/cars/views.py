from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.cars.forms import CarForm, CarPricingForm
from apps.cars.models import Car
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
        if brand:
            qs = qs.filter(brand__icontains=brand)
        if model:
            qs = qs.filter(model__icontains=model)
        if fuel_type:
            qs = qs.filter(fuel_type=fuel_type)
        return qs


class CarDetailView(DetailView):
    template_name = "cars/car_detail.html"
    model = Car
    context_object_name = "car"


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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pricing_form = context["pricing_form"]
        if not pricing_form.is_valid():
            return self.form_invalid(form)
        self.object = form.save()
        pricing = pricing_form.save(commit=False)
        pricing.car = self.object
        pricing.save()
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
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        pricing_form = context["pricing_form"]
        if not pricing_form.is_valid():
            return self.form_invalid(form)
        self.object = form.save()
        pricing = pricing_form.save(commit=False)
        pricing.car = self.object
        pricing.save()
        messages.success(self.request, "Car updated.")
        return redirect(self.success_url)


class ManagerCarDeleteView(ManagerRequiredMixin, DeleteView):
    model = Car
    success_url = reverse_lazy("manager-car-list")
    template_name = "cars/manager_car_confirm_delete.html"
