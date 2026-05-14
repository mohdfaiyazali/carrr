from django import forms

from apps.bookings.models import Booking
from apps.drivers.models import Driver


class BookingApprovalForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["driver"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["driver"].required = False
        self.fields["driver"].queryset = Driver.objects.filter(status=Driver.Status.AVAILABLE, is_active=True)
