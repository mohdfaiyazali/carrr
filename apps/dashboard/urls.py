from django.urls import path

from apps.dashboard.views import ManagerDashboardView

urlpatterns = [
    path("manager/dashboard/", ManagerDashboardView.as_view(), name="manager-dashboard"),
]
