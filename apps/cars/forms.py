from django import forms

from apps.cars.models import Car, CarPricing


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            "brand",
            "model",
            "year",
            "color",
            "fuel_type",
            "transmission",
            "seating_capacity",
            "description",
            "is_driver_available",
            "status",
        ]


class CarPricingForm(forms.ModelForm):
    class Meta:
        model = CarPricing
        fields = ["hourly_rate", "half_day_rate", "full_day_rate", "per_day_rate"]


class CarImageUploadForm(forms.Form):
    images = MultipleFileField(required=False)
