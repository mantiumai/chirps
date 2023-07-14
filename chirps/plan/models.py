"""Models for the plan application."""
from django.contrib.auth.models import User
from django.db import models


class Plan(models.Model):
    """Model for what to do when scanning a target."""

    # True to hide this plan from the user
    archived = models.BooleanField(default=False)

    name = models.CharField(max_length=256)
    description = models.TextField()

    # True if this plan is a template for other plans
    is_template = models.BooleanField(default=False)

    # Bind this plan to a user if it isn't a template
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # The current version of the plan
    current_version = models.ForeignKey(
        'PlanVersion', on_delete=models.CASCADE, related_name='current_version', null=True, blank=True
    )

    def __str__(self):
        """Stringify the name"""
        return self.name


class PlanVersion(models.Model):
    """Model to track a revision of the plan."""

    number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)


class Rule(models.Model):
    """A step to execute within a plan."""

    name = models.CharField(max_length=256)

    # Query to run against the target
    query_string = models.TextField()

    # Embedding of the query string
    query_embedding = models.TextField(null=True, blank=True)

    # Regular expression to run against the response documents
    regex_test = models.TextField()

    # If the regex test finds results in the response documents, how severe of a problem is it?
    severity = models.IntegerField()

    # Foreign Key to the plan this rule belongs to
    plan = models.ForeignKey(PlanVersion, on_delete=models.CASCADE, related_name='rules')

    def __str__(self):
        """Stringify the name"""
        return self.name
