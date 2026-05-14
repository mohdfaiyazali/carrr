from django.urls import path

from apps.drivers.views import (
    ManagerDriverCreateView,
    ManagerDriverDeleteView,
    ManagerDriverListView,
    ManagerDriverUpdateView,
)

urlpatterns = [
    path("manager/drivers/", ManagerDriverListView.as_view(), name="manager-driver-list"),
    path("manager/drivers/new/", ManagerDriverCreateView.as_view(), name="manager-driver-create"),
    path("manager/drivers/<int:pk>/edit/", ManagerDriverUpdateView.as_view(), name="manager-driver-update"),
    path("manager/drivers/<int:pk>/delete/", ManagerDriverDeleteView.as_view(), name="manager-driver-delete"),
]
