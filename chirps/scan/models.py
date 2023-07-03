"""Models for the scan application."""
import json
from django.contrib import admin
from django.db import models
from django_celery_results.models import TaskResult
from plan.models import Rule
from django.contrib.auth.models import User

class Scan(models.Model):
    """Model for a single scan run against a target."""

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True)
    description = models.TextField()
    plan = models.ForeignKey('plan.Plan', on_delete=models.CASCADE)
    target = models.ForeignKey('target.BaseTarget', on_delete=models.CASCADE)
    results = models.ManyToManyField('scan.Result', blank=True)
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

    count = models.SmallIntegerField()
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    result = models.BooleanField()
    details = models.TextField(null=True, blank=True, default='{}')  


admin.site.register(Scan)
admin.site.register(Result)
