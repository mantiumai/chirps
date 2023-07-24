"""Forms for rendering scan application models."""
from django import forms
from django.forms import ModelForm, ValidationError
from policy.models import Policy

from .models import Scan


class ScanForm(ModelForm):
    """Form for the main scan model."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        # self.fields['policies'].label = 'Policies'
        super().__init__(*args, **kwargs)

    # Add a MultipleChoiceField for policies with CheckboxSelectMultiple widget
    policies = forms.ModelMultipleChoiceField(
        queryset=Policy.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': 'true', 'data-size': '10'}),
        required=True,
    )

    class Meta:
        """Django Meta options for the ScanForm."""

        model = Scan
        fields = ['target', 'description']

        widgets = {
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}
            ),
            'target': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """Create the 'policies' cleaned data field."""
        super().clean()
        self.cleaned_data['policies'] = []

        # Policies were not passed in - bad!
        if 'policies' not in self.data.keys():
            raise ValidationError('No policies selected')

        for policy_id in self.data.getlist('policies'):
            try:
                policy = Policy.objects.get(id=policy_id, user=self.user)
                self.cleaned_data['policies'].append(policy)
            except Policy.DoesNotExist:
                raise ValidationError('Invalid policies selected')
