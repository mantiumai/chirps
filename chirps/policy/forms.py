"""Forms for the Policy app."""
from django import forms

from .models import Policy, RuleTypes


class PolicyForm(forms.Form):
    """Form for creating a new policy."""

    name = forms.CharField(label='Policy Name', max_length=100)
    description = forms.CharField(label='Policy Description', max_length=1000)

    def _rule_field_id(self, field_name: str, rule_id: int) -> str:
        """Build a unique ID for a rule field."""
        return f'rule_{field_name}_{rule_id}'

    def clean(self):
        """Create the 'rules' cleaned data field."""
        super().clean()
        rules = []

        # Walk through all of the field keys, building a rule for each one
        for rule_id in self.get_form_field_keys():
            rule = {}

            rule_type = rule_id.split('_')[0]
            rule['name'] = self.data[self._rule_field_id('name', rule_id)]
            rule['severity'] = self.data[self._rule_field_id('severity', rule_id)]
            rule['type'] = rule_type

            if rule_type == RuleTypes.REGEX.value:
                rule['query_string'] = self.data[self._rule_field_id('query_string', rule_id)]
                rule['regex_test'] = self.data[self._rule_field_id('regex_test', rule_id)]
            elif rule_type == RuleTypes.MULTIQUERY.value:
                rule['task_description'] = self.data[self._rule_field_id('task_description', rule_id)]
                rule['acceptable_outcomes'] = self.data[self._rule_field_id('acceptable_outcomes', rule_id)]

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
