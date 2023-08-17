"""Severity forms"""
from django import forms
from severity.models import Severity


class CreateSeverityForm(forms.ModelForm):
    """Form for creating a new severity."""

    class Meta:
        model = Severity
        fields = ['name', 'value', 'color']
        widgets = {'color': forms.widgets.TextInput(attrs={'type': 'color'})}


class EditSeverityForm(CreateSeverityForm):
    """Form for editing an existing severity."""
