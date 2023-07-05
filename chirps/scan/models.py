"""Models for the scan application."""
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django_celery_results.models import TaskResult
from fernet_fields import EncryptedTextField

from plan.models import Rule


class Scan(models.Model):
    """Model for a single scan run against a target."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    description = models.TextField()
    plan = models.ForeignKey('plan.Plan', on_delete=models.CASCADE)
    target = models.ForeignKey('target.BaseTarget', on_delete=models.CASCADE)
    celery_task_id = models.CharField(max_length=256, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.description

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

    # The scan that the result belongs to
    scan = models.ForeignKey(Scan, on_delete=models.CASCADE)

    # The raw text (encrypted at REST) that was scanned
    text = EncryptedTextField()

    # The rule that was used to scan the text
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.rule.name} - {self.scan.id}'

class Finding(models.Model):
    """Model to identify the location of a finding within a result."""

    result = models.ForeignKey(Result, on_delete=models.CASCADE)
    offset = models.IntegerField()
    length = models.IntegerField()

    def __str__(self):
        return f'{self.offset}:{self.length}'

    def text(self):
        """Return the text of the finding."""
        return self.result.text[self.offset:self.offset + self.length]

    def surrounding_text(self):
        """return the text of the finding, with some surrounding context."""
        buffer = self.result.text[self.offset - 20: self.offset - 1]
        buffer += "<span class='text-danger'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += "</span>"
        buffer += self.result.text[self.offset + self.length + 1: self.offset + self.length + 19]
        return mark_safe(buffer)

    def with_highlight(self):
        """return the entire text searched by the finding's rule - highlight the finding."""
        buffer = self.result.text[0 : self.offset - 1]
        buffer += "<span class='bg-danger text-white'>"
        buffer += self.result.text[self.offset : self.offset + self.length]
        buffer += "</span>"
        buffer += self.result.text[self.offset + self.length + 1 : ]
        return mark_safe(buffer)
