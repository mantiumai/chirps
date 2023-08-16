"""Forms for the Policy app."""
from django import forms

from .models import Policy, Severity


class PolicyForm(forms.Form):
    """Form for creating a new policy."""

    name = forms.CharField(label='Policy Name', max_length=100)
    description = forms.CharField(label='Policy Description', max_length=1000)

    def clean(self):
        """Create the 'rules' cleaned data field."""
        super().clean()
        rules = []

        # For each of the form field IDs, build a list of Rules
        rule_key_prefixes = ['rule_name', 'rule_query_string', 'rule_regex', 'rule_severity']

        # Walk through all of the field keys, building a rule for each one
        for rule_id in self.get_form_field_keys():
            rule = {}

            # Walk through all of the key prefixes, adding them to the rule dictionary
            # The key for the rule dictionary is JUST the prefix, not the prefix + rule ID
            for prefix in rule_key_prefixes:
                rule[f'{prefix}'] = self.data[f'{prefix}_{rule_id}']

            # Add the rule to the list of rules
            rules.append(rule)

        self.cleaned_data['rules'] = rules

    def get_form_field_keys(self) -> list[str]:
        """Given the uncleaned data, return a list of unique IDs for each rule field."""
        keys: list[str] = []

        for key in self.data.keys():
            if key.startswith('rule_name_'):
                keys.append(key.removeprefix('rule_name_'))

        return keys

    @classmethod
    def from_policy(cls, policy: Policy) -> 'PolicyForm':
        """Construct"""
        index = 0
        data = {'name': policy.name, 'description': policy.description}

        # Push all of the rules from the current policy into the dictionary
        for rule in policy.current_version.rules.all():
            data[f'rule_name_{index}'] = rule.name
            data[f'rule_query_string_{index}'] = rule.query_string
            data[f'rule_regex_{index}'] = rule.regex_test
            data[f'rule_severity_{index}'] = rule.severity
            index += 1

        return PolicyForm(data=data)


class CreateSeverityForm(forms.ModelForm):
    """Form for creating a new severity."""

    class Meta:
        model = Severity
        fields = ['name', 'value', 'color']


class EditSeverityForm(forms.ModelForm):
    """Form for editing an existing severity."""

    class Meta:
        model = Severity
        fields = ['name', 'value', 'color']
