from django.urls import path

from apps.cars.views import CarDetailView, CarListView

urlpatterns = [
    path("", CarListView.as_view(), name="car-list"),
    path("<int:pk>/", CarDetailView.as_view(), name="car-detail"),
]
