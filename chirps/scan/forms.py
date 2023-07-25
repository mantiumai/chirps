"""Forms for rendering scan application models."""
from django import forms
from django.forms import ModelForm, ValidationError
from policy.models import Policy
from target.models import BaseTarget

from .models import Scan


class ScanForm(ModelForm):
    """Form for the main scan model."""

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
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
        fields = ['description']

        widgets = {
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}
            ),
        }

    def clean(self):
        """Create the 'policies' and 'targets' cleaned data fields."""
        super().clean()
        self.cleaned_data['policies'] = []

        if 'policies' not in self.data.keys():
            raise ValidationError('No policies selected')

        for policy_id in self.data.getlist('policies'):
            try:
                policy = Policy.objects.get(id=policy_id)

                if policy.is_template or policy.user == self.user:
                    self.cleaned_data['policies'].append(policy)
                else:
                    raise ValidationError('User does not have access to selected policy')

            except Policy.DoesNotExist as exc:
                raise ValidationError('Invalid policies selected') from exc

        self.cleaned_data['targets'] = []

        # Targets were not passed in - bad!
        if 'targets' not in self.data.keys():
            raise ValidationError('No target(s) selected')

        for target_id in self.data.getlist('targets'):
            try:
                target = BaseTarget.objects.get(id=target_id, user=self.user)
                self.cleaned_data['targets'].append(target)
            except BaseTarget.DoesNotExist:
                raise ValidationError('Invalid target(s) selected')
