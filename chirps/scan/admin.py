"""Registration point of the admin interface for the scan app."""
from django.contrib import admin

from .models import Finding, Result, ScanAsset, ScanAssetFailure, ScanRun, ScanTemplate

admin.site.register(ScanTemplate)
admin.site.register(ScanRun)
admin.site.register(Result)
admin.site.register(Finding)
admin.site.register(ScanAsset)
admin.site.register(ScanAssetFailure)
