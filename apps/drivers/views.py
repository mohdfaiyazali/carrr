from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.core.mixins import ManagerRequiredMixin
from apps.drivers.forms import DriverForm
from apps.drivers.models import Driver


class ManagerDriverListView(ManagerRequiredMixin, ListView):
    template_name = "drivers/manager_driver_list.html"
    context_object_name = "drivers"
    model = Driver


class ManagerDriverCreateView(ManagerRequiredMixin, CreateView):
    model = Driver
    form_class = DriverForm
    template_name = "drivers/manager_driver_form.html"
    success_url = reverse_lazy("manager-driver-list")


class ManagerDriverUpdateView(ManagerRequiredMixin, UpdateView):
    model = Driver
    form_class = DriverForm
    template_name = "drivers/manager_driver_form.html"
    success_url = reverse_lazy("manager-driver-list")


class ManagerDriverDeleteView(ManagerRequiredMixin, DeleteView):
    model = Driver
    template_name = "drivers/manager_driver_confirm_delete.html"
    success_url = reverse_lazy("manager-driver-list")
