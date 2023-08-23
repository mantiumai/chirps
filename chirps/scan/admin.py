"""Registration point of the admin interface for the scan app."""
from django.contrib import admin

from .models import RegexFinding, RegexResult, ScanAsset, ScanAssetFailure, ScanRun, ScanTemplate, ScanVersion

admin.site.register(ScanTemplate)
admin.site.register(ScanRun)
admin.site.register(ScanVersion)
admin.site.register(RegexResult)
admin.site.register(RegexFinding)
admin.site.register(ScanAsset)
admin.site.register(ScanAssetFailure)
