from django import forms

from .models import SpecialOpeningHours


class SpecialOpeningHoursForm(forms.ModelForm):
    class Meta:
        model = SpecialOpeningHours
        fields = ("date", "closed", "opens_at", "closes_at", "description")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "opens_at": forms.TimeInput(attrs={"type": "time"}),
            "closes_at": forms.TimeInput(attrs={"type": "time"}),
        }
