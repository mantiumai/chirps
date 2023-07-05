"""Admin interface definition for plan models."""
from django.contrib import admin

from .models import Plan, Rule

admin.site.register(Plan)
admin.site.register(Rule)
