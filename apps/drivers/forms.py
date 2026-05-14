from django import forms

from apps.drivers.models import Driver


class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ["name", "phone", "license_number", "experience_years", "status", "driver_hourly_rate", "is_active"]
