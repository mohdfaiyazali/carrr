from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.users.forms import CustomerSignUpForm
from apps.users.models import User


class RoleBasedLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.role in [User.Role.MANAGER, User.Role.ADMIN] or user.is_superuser:
            return reverse_lazy("manager-dashboard")
        return reverse_lazy("home")


class CustomerSignUpView(CreateView):
    form_class = CustomerSignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.CUSTOMER
        user.save()
        login(self.request, user)
        messages.success(self.request, "Account created successfully.")
        return redirect(self.success_url)
