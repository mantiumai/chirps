"""Admin interface definition for policy models."""
from django.contrib import admin

from .models import MultiQueryRule, Policy, PolicyVersion, RegexRule

admin.site.register(Policy)
admin.site.register(PolicyVersion)
admin.site.register(RegexRule)
admin.site.register(MultiQueryRule)
