"""Celery tasks for the scan application."""
import re
from logging import getLogger

from celery import shared_task
from django.utils import timezone
from embedding.utils import create_embedding
from target.models import BaseTarget

from .models import Finding, Result, ScanTarget

logger = getLogger(__name__)


@shared_task
def scan_task(scan_target_id):
    """Scan task."""
    logger.info('Starting scan task', extra={'scan_target_id': scan_target_id})

    try:
        scan_target = ScanTarget.objects.get(pk=scan_target_id)
        scan = scan_target.scan

        # Update scan status
        scan.status = 'Running'
        scan.save()

    except ScanTarget.DoesNotExist:
        logger.error('ScanTarget record not found', extra={'scan_target_id': scan_target_id})
        scan_task.update_state(state='FAILURE', meta={'error': f'ScanTarget record not found ({scan_target_id})'})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    target = BaseTarget.objects.get(id=scan_target.target.id)

    # Iterate through the selected policies and fetch their rules
    policy_rules = []
    for policy in scan.policies.all():
        for rule in policy.current_version.rules.all():
            policy_rules.append(rule)

    total_rules = len(policy_rules)
    rules_run = 0
    for rule in policy_rules:
        logger.info('Starting rule evaluation', extra={'id': rule.id})

        if target.REQUIRES_EMBEDDINGS:
            embedding = create_embedding(
                rule.query_string, target.embedding_model, target.embedding_model_service, scan.user
            )
            query = embedding.vectors
        else:
            query = rule.query_string
        results = target.search(query, max_results=100)

        for text in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = Result(rule=rule, text=text, scan_target=scan_target)
            result.save()

            # Run the regex against the text
            for match in re.finditer(rule.regex_test, text):

                # Persist the finding
                finding = Finding(result=result, offset=match.start(), length=match.end() - match.start())
                finding.save()

        # Update the progress counter based on the number of rules that have been evaluated
        rules_run += 1
        scan_target.progress = int(rules_run / total_rules * 100)
        scan_target.save()

    # Persist the completion time of the scan
    scan_target.finished_at = timezone.now()
    scan_target.save()

    logger.info('Scan task complete', extra={'scan_target_id': scan_target.id})

    # If any of the scan targets are running, skip setting the main scan status to complete
    for scan_target in scan.scan_targets.all():
        if scan_target.finished_at is None:
            return

    scan.status = 'Complete'
    scan.finished_at = timezone.now()
    scan.save()

    logger.info('Scan complete', extra={'scan_id': scan.id})
