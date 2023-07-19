"""Forms for rendering scan application models."""
from django import forms
from django.forms import ModelForm

from .models import Scan


class ScanForm(ModelForm):
    """Form for the main scan model."""

    class Meta:
        """Django Meta options for the ScanForm."""

        model = Scan
        fields = ['description', 'target', 'policy']

        widgets = {
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}
            ),
            'target': forms.Select(attrs={'class': 'form-control'}),
            'policy': forms.Select(attrs={'class': 'form-control'}),
        }
