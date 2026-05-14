from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.users.views import CustomerSignUpView, RoleBasedLoginView

urlpatterns = [
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", CustomerSignUpView.as_view(), name="register"),
]
