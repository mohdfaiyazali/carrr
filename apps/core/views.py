from django.views.generic import TemplateView

from apps.cars.models import Car


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cars"] = Car.objects.filter(status=Car.Status.AVAILABLE)[:6]
        return context
