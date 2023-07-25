"""Models for the scan application."""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django_celery_results.models import TaskResult
from fernet_fields import EncryptedTextField
from policy.models import Rule
from target.models import BaseTarget


class Scan(models.Model):
    """Model for a single scan run against a target."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    description = models.TextField()
    policies = models.ManyToManyField('policy.Policy')
    celery_task_id = models.CharField(max_length=256, null=True)
    progress = models.IntegerField(default=0)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(
        max_length=32,
        default='Queued',
        choices=[('Queued', 'Queued'), ('Running', 'Running'), ('Complete', 'Complete'), ('Failed', 'Failed')],
    )

    def __str__(self) -> str:
        """Stringify the description"""
        return self.description

    def progress(self):
        """Compute the progress of the scan."""
        value_count = 0
        value = 0

        for scan_target in self.scan_targets.all():
            value += scan_target.progress
            value_count += 1

        return int(value / value_count)

    def duration(self):
        """Calculate the duration the scan has run."""
        if self.finished_at and self.started_at:
            return self.finished_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        else:
            return 'N/A'

    def target_count(self):
        """Fetch the number of scan targets associated with this scan."""
        return ScanTarget.objects.filter(scan=self).count()

    def findings_count(self) -> int:
        """Fetch the number of findings associated with this scan."""
        count = 0
        scan_targets = ScanTarget.objects.filter(scan=self)
        for scan_target in scan_targets:

            # Iterate through the rule set
            for result in scan_target.results.all():
                count += result.findings_count()

        return count


class ScanTarget(models.Model):
    """Model for a single target that was scanned."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name='scan_targets')
    target = models.ForeignKey(BaseTarget, on_delete=models.CASCADE)
    celery_task_id = models.CharField(max_length=256, null=True)
    progress = models.IntegerField(default=0)

    def __str__(self) -> str:
        """Stringify the target name"""
        return self.target.name

    def celery_task_status(self) -> str:
        """Fetch the status of the Celery task associated with this scan."""
        if self.celery_task_id is None:
            return 'N/A'

        # We're using the Django Celery Results backend, so we can query the results from there
        result = TaskResult.objects.get(task_id=self.celery_task_id)
        return result.status

    def celery_task_output(self) -> str:
        """Fetch the output of the Celery task associated with this scan."""
        if self.celery_task_id is None:
            return 'N/A'

        # We're using the Django Celery Results backend, so we can query the results from there
        result = TaskResult.objects.get(task_id=self.celery_task_id)
        return result.result


class Result(models.Model):
    """Model for a single result from a rule."""

    # Scan target that the result belongs to
    scan_target = models.ForeignKey(ScanTarget, on_delete=models.CASCADE, related_name='results')

    # The raw text (encrypted at REST) that was scanned
    text = EncryptedTextField()

    # The rule that was used to scan the text
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)

    def has_findings(self) -> bool:
        """Return True if the result has findings, False otherwise."""
        if self.findings_count():
            return True

        return False

    def findings_count(self) -> int:
        """Return the number of findings associated with this result."""
        findings_query = Finding.objects.filter(result=self)
        return findings_query.count()

    def __str__(self):
        """Stringify the rule name and scan ID"""
        return f'{self.rule.name} - {self.scan_target.scan.id}'


class Finding(models.Model):
    """Model to identify the location of a finding within a result."""

    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='findings')
    offset = models.IntegerField()
    length = models.IntegerField()

    def __str__(self):
        """Stringify the offset and length separated by a colon"""
        return f'{self.offset}:{self.length}'

    def text(self):
        """Return the text of the finding."""
        return self.result.text[self.offset : self.offset + self.length]

    def surrounding_text(self):
        """return the text of the finding, with some surrounding context."""
        buffer = self.result.text[self.offset - 20 : self.offset - 1]
        buffer += "<span class='text-danger'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 : self.offset + self.length + 19]
        return mark_safe(buffer)

    def with_highlight(self):
        """return the entire text searched by the finding's rule - highlight the finding."""
        buffer = self.result.text[0 : self.offset - 1]
        buffer += "<span class='bg-danger text-white'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += '</span>'
        buffer += self.result.text[self.offset + self.length + 1 :]
        return mark_safe(buffer)
