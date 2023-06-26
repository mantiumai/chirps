from django import forms
from django.forms import ModelForm
from target.models import BaseTarget

from .models import Scan


class ScanForm(ModelForm):
    class Meta:
        model = Scan
        fields = ['description', 'target', 'plan']

        widgets = {
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}
            ),
        }
