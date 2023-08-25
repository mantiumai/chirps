"""Models for the policy application."""
import json
from typing import Any

from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from polymorphic.models import PolymorphicModel
from severity.models import Severity


class Policy(models.Model):
    """Model for what to do when scanning an asset."""

    # True to hide this policy from the user
    archived = models.BooleanField(default=False)

    name = models.CharField(max_length=256)
    description = models.TextField()

    # True if this policy is a template for other policies
    is_template = models.BooleanField(default=False)

    # Bind this policy to a user if it isn't a template
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # The current version of the policy
    current_version = models.ForeignKey(
        'PolicyVersion', on_delete=models.CASCADE, related_name='current_version', null=True, blank=True
    )

    def __str__(self):
        """Stringify the name"""
        return self.name


class PolicyVersion(models.Model):
    """Model to track a revision of the policy."""

    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)


class BaseRule(PolymorphicModel):
    """Base class that all rules will inherit from."""

    name = models.CharField(max_length=256)

    rule_type = None

    # ForeignKey relationship to the Severity model
    severity = models.ForeignKey(Severity, on_delete=models.CASCADE)

    # Foreign Key to the policy this rule belongs to
    policy = models.ForeignKey(PolicyVersion, on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        """Stringify the name"""
        return self.name


class RegexRule(BaseRule):
    """A step to execute within a policy."""

    rule_type = 'regex'
    edit_template = 'policy/edit_regex_rule.html'
    create_template = 'policy/create_regex_rule.html'

    # Query to run against the asset
    query_string = models.TextField()

    # Embedding of the query string
    query_embedding = models.TextField(null=True, blank=True)

    # Regular expression to run against the response documents
    regex_test = models.TextField()


class MultiQueryRule(BaseRule):
    """Multi-query rule."""

    rule_type = 'multiquery'
    edit_template = 'policy/edit_multiquery_rule.html'
    create_template = 'policy/create_multiquery_rule.html'

    # Description of the task to be completed
    task_description = models.TextField()

    # Acceptable outcomes of the task
    acceptable_outcomes = models.TextField(validators=[validate_comma_separated_integer_list])

    def set_acceptable_outcomes(self, outcomes_list):
        """Set the acceptable outcomes for the rule."""
        self.acceptable_outcomes = json.dumps(outcomes_list)

    def get_acceptable_outcomes(self):
        """Get the acceptable outcomes for the rule."""
        return json.loads(self.acceptable_outcomes)


def rule_classes(base_class: Any) -> dict[str, type]:
    """Get all subclasses of a given class recursively."""
    subclasses_dict = {}
    for subclass in base_class.__subclasses__():
        subclasses_dict[subclass.rule_type] = subclass
        subclasses_dict.update(rule_classes(subclass))
    return subclasses_dict


RULES = rule_classes(BaseRule)
