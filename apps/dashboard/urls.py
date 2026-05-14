from django.urls import path

from apps.dashboard.views import CustomerDashboardView, ManagerDashboardView

urlpatterns = [
    path("dashboard/", CustomerDashboardView.as_view(), name="customer-dashboard"),
    path("manager/dashboard/", ManagerDashboardView.as_view(), name="manager-dashboard"),
]
