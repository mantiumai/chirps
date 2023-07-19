"""Forms for rendering scan application models."""
from django import forms
from django.forms import ModelForm

from .models import Scan
from policy.models import Policy


class ScanForm(ModelForm):  
    """Form for the main scan model."""  
    # Add a MultipleChoiceField for policies with CheckboxSelectMultiple widget
    policies = forms.ModelMultipleChoiceField(
        queryset=Policy.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
    )  
  
    class Meta:  
        """Django Meta options for the ScanForm."""  
        model = Scan  
        fields = ['description', 'target']  
  
        widgets = {  
            'description': forms.TextInput(  
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}  
            ),  
            'target': forms.Select(attrs={'class': 'form-control'}),  
        }  

    def __init__(self, *args, **kwargs):
        super(ScanForm, self).__init__(*args, **kwargs)
        self.fields['policies'].label = 'Policies'
