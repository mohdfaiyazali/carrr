from django.views.generic import DetailView, ListView

from apps.cars.models import Car


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
