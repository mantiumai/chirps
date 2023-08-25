"""Models for the scan application."""
from abc import abstractmethod

from asset.models import BaseAsset
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_celery_results.models import TaskResult
from fernet_fields import EncryptedTextField
from policy.models import BaseRule, RegexRule


class ScanTemplate(models.Model):
    """Model for a single scan run against an asset."""

    name = models.CharField(max_length=256)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    # The current version of the scan
    current_version = models.ForeignKey(
        'ScanVersion', on_delete=models.CASCADE, related_name='current_version', null=True, blank=True
    )

    def __str__(self) -> str:
        """Stringify the description"""
        return self.description

    def policy_count(self):
        """Fetch the number of policies associated with this scan."""
        return self.current_version.policies.count()

    def asset_count(self):
        """Fetch the number of assets associated with this scan."""
        return self.current_version.assets.count()

    def assets(self):
        """Fetch a list of all the assets associated with this scan."""
        return self.current_version.assets.all()

    def policies(self):
        """Fetch a list of all the policies associated with this scan."""
        return self.current_version.policies.all()

    def run_count(self):
        """Fetch the number of runs associated with this scan."""
        return self.current_version.scan_runs.count()

    def is_running(self):
        """Detect if the scan has any ScanRun objects in the Running state."""
        for scan_run in self.current_version.scan_runs.all():
            if scan_run.is_running():
                return True

        return False

    def progress(self):
        """Compute the progress of the scan."""
        value_count = 0
        value = 0

        for scan_asset in self.current_version.scan_run_assets.all():
            value += scan_asset.progress
            value_count += 1

        try:   # Avoid divide by zero
            return int(value / value_count)
        except ZeroDivisionError:
            return 0


class ScanVersion(models.Model):
    """Models a single version of a scan."""

    number = models.IntegerField(default=1)
    scan = models.ForeignKey(ScanTemplate, on_delete=models.CASCADE, related_name='versions')
    policies = models.ManyToManyField('policy.Policy')
    assets = models.ManyToManyField(BaseAsset, related_name='scan_assets')


class ScanRun(models.Model):
    """Models a singular run of a versioned scan."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    scan_version = models.ForeignKey(ScanVersion, on_delete=models.CASCADE, related_name='scan_runs')

    status = models.CharField(
        max_length=32,
        default='Queued',
        choices=[
            ('Queued', 'Queued'),
            ('Running', 'Running'),
            ('Complete', 'Complete'),
            ('Failed', 'Failed'),
            ('Canceled', 'Canceled'),
        ],
    )

    def is_running(self):
        """Determine if the scan is either running or queued."""
        if self.status in ['Running', 'Queued']:
            return True

        return False

    def duration(self):
        """Calculate the duration the scan has run."""
        if self.finished_at and self.started_at:
            return self.finished_at - self.started_at

        if self.started_at:
            return timezone.now() - self.started_at

        return 'N/A'

    def findings_count(self) -> int:
        """Fetch the number of findings associated with this scan."""
        count = 0
        scan_assets = ScanAsset.objects.filter(scan=self)
        for scan_asset in scan_assets:

            # Iterate through the rule set
            for result in scan_asset.results.all():
                count += result.findings_count()

        return count


class ScanAsset(models.Model):
    """Model for a single asset that was scanned."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    scan = models.ForeignKey(ScanRun, on_delete=models.CASCADE, related_name='run_assets')
    asset = models.ForeignKey(BaseAsset, on_delete=models.CASCADE, related_name='scan_run_assets')
    celery_task_id = models.CharField(max_length=256, null=True)
    progress = models.IntegerField(default=0)

    def __str__(self) -> str:
        """Stringify the asset name"""
        return self.asset.name

    def celery_task_status(self) -> str:
        """Fetch the status of the Celery task associated with this scan."""
        if self.celery_task_id is None:
            return 'N/A'

        # We're using the Django Celery Results backend, so we can query the results from there
        try:
            result = TaskResult.objects.get(task_id=self.celery_task_id)
        except TaskResult.DoesNotExist:
            return 'Unable to get Celery task status'

        return result.status

    def celery_task_output(self) -> str:
        """Fetch the output of the Celery task associated with this scan."""
        if self.celery_task_id is None:
            return 'N/A'

        # We're using the Django Celery Results backend, so we can query the results from there
        result = TaskResult.objects.get(task_id=self.celery_task_id)
        return result.result

    def failure_text(self):
        """Fetch the failure text of the Celery task associated with this scan."""
        if self.celery_task_id is None:
            return 'N/A'

        try:
            failure = ScanAssetFailure.objects.get(scan_asset=self)
            return failure.traceback
        except ScanAssetFailure.DoesNotExist:
            return 'N/A'

        return 'N/A'


class ScanAssetFailure(models.Model):
    """Model to store data for a scan asset failure."""

    created_at = models.DateTimeField(auto_now_add=True)
    scan_asset = models.ForeignKey(ScanAsset, on_delete=models.CASCADE, related_name='failures')
    exception = models.TextField()
    traceback = models.TextField()


class BaseResult(models.Model):
    """Base model for a single result from a rule."""

    # Scan asset that the result belongs to
    scan_asset = models.ForeignKey(ScanAsset, on_delete=models.CASCADE, related_name='results')

    # The rule that was used to scan the text
    rule = models.ForeignKey(BaseRule, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def has_findings(self) -> bool:
        """Return True if the result has findings, False otherwise."""
        if self.findings_count():
            return True

        return False

    @abstractmethod
    def findings_count(self) -> int:
        """Return the number of findings associated with this result."""
        raise NotImplementedError

    def __str__(self):
        """Stringify the rule name and scan ID"""
        return f'{self.rule.name} - {self.scan_asset.scan.id}'


class RegexResult(BaseResult):
    """Model for a single result from a Regex rule."""

    # The rule that was used to scan the text
    rule = models.ForeignKey(RegexRule, on_delete=models.CASCADE)

    # The raw text (encrypted at REST) that was scanned
    text = EncryptedTextField()

    def findings_count(self) -> int:
        """Return the number of findings associated with this result."""
        findings_query = self.findings.filter(result=self)
        return findings_query.count()


class BaseFinding(models.Model):
    """Base model to identify the location of a finding within a result."""

    result = models.ForeignKey(BaseResult, on_delete=models.CASCADE, related_name='findings')

    class Meta:
        abstract = True

    def __str__(self):
        """Stringify the finding"""
        return f'{self.result}'


class RegexFinding(BaseFinding):
    """Model to identify the location of a finding within a Regex result."""

    result = models.ForeignKey(RegexResult, on_delete=models.CASCADE, related_name='findings')
    source_id = models.TextField(blank=True, null=True)
    offset = models.IntegerField()
    length = models.IntegerField()

    def text(self):
        """Return the text of the finding."""
        return self.result.text[self.offset : self.offset + self.length]

    def surrounding_text(self, preview_size: int = 20):
        """return the text of the finding, with some surrounding context."""
        buffer = self.result.text[self.offset - preview_size : self.offset - 1]
        buffer += "<span class='text-danger'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 : self.offset + self.length + preview_size - 1]
        return mark_safe(buffer)

    def with_highlight(self):
        """return the entire text searched by the finding's rule - highlight the finding."""
        buffer = self.result.text[0 : self.offset - 1]
        buffer += "<span class='bg-danger text-white'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 :]
        return mark_safe(buffer)
