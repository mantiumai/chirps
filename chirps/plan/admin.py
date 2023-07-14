"""Admin interface definition for plan models."""
from django.contrib import admin

from .models import Plan, PlanVersion, Rule

admin.site.register(Plan)
admin.site.register(PlanVersion)
admin.site.register(Rule)
