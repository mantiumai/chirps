"""Celery tasks for the scan application."""
from logging import getLogger
import re

from celery import shared_task
from django.utils import timezone
from target.models import BaseTarget

from .models import Finding, Result, Scan

logger = getLogger(__name__)

@shared_task
def scan_task(scan_id):
    """Main scan task."""

    logger.info('Starting scan',  extra={'id': scan_id})

    try:
        scan = Scan.objects.get(pk=scan_id)
    except Scan.DoesNotExist:
        logger.error('Scan record not found', extra={'id': scan_id})

        scan_task.update_state(state='FAILURE',
                               meta={'error': f'Scan record not found ({scan_id})'})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    target = BaseTarget.objects.get(id=scan.target.id)

    # Now that we have the derrived class, call its implementation of search()
    for rule in scan.plan.rules.all():
        logger.info('Starting rule evaluation', extra={'id': rule.id})
        results = target.search(query=rule.query_string, max_results=100)

        for text in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = Result(rule=rule, text=text, scan=scan)
            result.save()

            # Run the regex against the text
            for match in re.finditer(rule.regex_test, text):

                # Persist the finding
                finding = Finding(result=result, offset=match.start(), length=match.end() - match.start())
                finding.save()

    # Persist the completion time of the scan
    scan.finished_at = timezone.now()
    scan.save()
    logger.info('Scan complete', extra={'id': scan_id})
