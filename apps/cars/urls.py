from django.urls import path

from apps.cars.views import CarDetailView, CarListView
from apps.cars.views import ManagerCarCreateView, ManagerCarDeleteView, ManagerCarListView, ManagerCarUpdateView

urlpatterns = [
    path("", CarListView.as_view(), name="car-list"),
    path("<int:pk>/", CarDetailView.as_view(), name="car-detail"),
    path("manager/cars/", ManagerCarListView.as_view(), name="manager-car-list"),
    path("manager/cars/new/", ManagerCarCreateView.as_view(), name="manager-car-create"),
    path("manager/cars/<int:pk>/edit/", ManagerCarUpdateView.as_view(), name="manager-car-update"),
    path("manager/cars/<int:pk>/delete/", ManagerCarDeleteView.as_view(), name="manager-car-delete"),
]
