from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView
from django.views.generic import TemplateView

from apps.cars.models import Car
from apps.core.forms import ContactForm


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.filter(status=Car.Status.AVAILABLE)[:6]
        return context


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm

    def form_valid(self, form):
        messages.success(self.request, "Thanks for contacting us. We received your message.")
        return redirect("contact")
