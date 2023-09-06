"""Forms for rendering scan application models."""
from asset.models import BaseAsset
from django import forms
from django.forms import ModelForm, ValidationError
from policy.models import Policy

from .models import ScanTemplate


class DateInput(forms.DateInput):
    """DateInput widget for the OneShotScanForm."""

    input_type = 'datetime-local'


class OneShotScanForm(forms.Form):
    """Form for scheduling a scan to run at some point in the future."""

    scan = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'selectpicker', 'data-live-search': 'true', 'data-size': '10'}),
    )

    start_on = forms.DateTimeField(widget=DateInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Only show scans that the user owns
        self.fields['scan'].queryset = ScanTemplate.objects.filter(user=self.user)


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

        model = ScanTemplate
        fields = ['name', 'description']
        labels = {'name': 'Name', 'description': 'Description'}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the scan'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter a description for the scan'}
            ),
        }

    @classmethod
    def from_scan(cls, scan: ScanTemplate) -> 'ScanForm':
        """Build a ScanForm from a ScanTemplate object."""
        data = {'name': scan.name, 'description': scan.description}

        # The policies and assets fields are a list of IDs, and not part of the standard form
        policies = [policy.id for policy in scan.policies()]
        assets = [asset.id for asset in scan.assets()]

        data['policies'] = Policy.objects.filter(id__in=policies)
        data['assets'] = BaseAsset.objects.filter(id__in=assets)

        return ScanForm(data=data)

    def clean(self):
        """Create the 'policies' and 'assets' cleaned data fields."""
        super().clean()

        def process_items(item_name, model_type, is_valid_item):
            """For a given form field name (item_name), perform a query to build objects that match."""
            items = []

            # If the required item is not in the POST data, raise an error
            if item_name not in self.data.keys():
                raise ValidationError(f'No {item_name}(s) selected')

            # For each item ID in the POST data, fetch it from the database
            for item_id in self.data.getlist(item_name):
                try:
                    item = model_type.objects.get(id=item_id)

                    # Double check that the item is valid (see the lambda's defined below)
                    if is_valid_item(item, self.user):
                        items.append(item)
                    else:
                        raise ValidationError(f'User does not have access to selected {item_name}')
                except model_type.DoesNotExist as exc:
                    raise ValidationError(f'Invalid {item_name}(s) selected') from exc
            return items

        def is_valid_policy(policy, user):
            """Check if the user owns the policy, or if it's a template."""
            return policy.is_template or policy.user == user

        def is_valid_asset(asset, user):
            """Check if the user owns the asset."""
            return asset.user == user

        self.cleaned_data['policies'] = process_items('policies', Policy, is_valid_policy)
        self.cleaned_data['assets'] = process_items('assets', BaseAsset, is_valid_asset)
