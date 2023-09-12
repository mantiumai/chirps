"""Forms for the Policy app."""
from django import forms
from embedding.models import Embedding

from .models import RULES, Policy


class PolicyForm(forms.Form):
    """Form for creating a new policy."""

    name = forms.CharField(label='Policy Name', max_length=100)
    description = forms.CharField(label='Policy Description', max_length=1000)

    def clean(self):
        """Create the 'rules' cleaned data field."""
        super().clean()
        rules = []

        for rule_id in self.get_form_field_keys():
            rule_type = self.data[f'rule_type_{rule_id}']
            rule_class = RULES[rule_type]
            rule_fields = {f.name: f for f in rule_class._meta.get_fields() if f.is_relation is False}

            rule = {
                'id': rule_id,
                'type': rule_type,
                'name': self.data[f'rule_name_{rule_id}'],
                'severity': self.data[f'rule_severity_{rule_id}'],
            }

            if rule_type == 'multiquery':
                rule['model_service'] = Embedding.get_service_from_model(self.data[f'rule_model_name_{rule_id}'])

            for field_name in rule_fields:
                if field_name not in ['id', 'name', 'severity', 'policy', 'rule_type', 'model_service']:
                    rule[field_name] = self.data[f'rule_{field_name}_{rule_id}']

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
        """Create a PolicyForm from a Policy object."""
        index = 0
        data = {'name': policy.name, 'description': policy.description}

        for rule in policy.current_version.rules.all():
            rule_type = rule.rule_type
            rule_class = RULES[rule_type]
            rule_fields = {f.name: f for f in rule_class._meta.get_fields() if f.is_relation is False}

            data[f'rule_type_{index}'] = rule_type
            data[f'rule_name_{index}'] = rule.name
            data[f'rule_severity_{index}'] = rule.severity
            data[f'rule_model_service_{index}'] = rule.model_service
            data[f'rule_model_name_{index}'] = rule.model_name

            for field_name in rule_fields:
                if field_name not in ['id', 'name', 'severity', 'policy', 'rule_type', 'model_service', 'model_name']:
                    data[f'rule_{field_name}_{index}'] = getattr(rule, field_name)

            index += 1

        return PolicyForm(data=data)
