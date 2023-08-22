"""Admin interface definition for policy models."""
from django.contrib import admin

from .models import Policy, PolicyVersion, RegexRule

admin.site.register(Policy)
admin.site.register(PolicyVersion)
admin.site.register(RegexRule)
