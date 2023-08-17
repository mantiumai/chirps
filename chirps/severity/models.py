"""Severity models"""
from django.db import models


class Severity(models.Model):
    """Model for severity levels."""

    name = models.CharField(max_length=64)
    value = models.PositiveIntegerField()
    color = models.CharField(max_length=7)
    archived = models.BooleanField(default=False)

    def __str__(self):
        """Stringify the name"""
        return self.name
