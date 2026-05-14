from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.users.models import User


class CustomerSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]
