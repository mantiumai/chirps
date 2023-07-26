"""Celery tasks for the scan application."""
import re
from logging import getLogger

from asset.models import BaseTarget
from celery import shared_task
from django.utils import timezone
from embedding.utils import create_embedding

from .models import Finding, Result, ScanTarget

logger = getLogger(__name__)


@shared_task
def scan_task(scan_asset_id):
    """Scan task."""
    logger.info('Starting scan task', extra={'scan_asset_id': scan_asset_id})

    try:
        scan_asset = ScanTarget.objects.get(pk=scan_asset_id)
        scan = scan_asset.scan

        # Update scan status
        scan.status = 'Running'
        scan.save()

    except ScanTarget.DoesNotExist:
        logger.error('ScanTarget record not found', extra={'scan_asset_id': scan_asset_id})
        scan_task.update_state(state='FAILURE', meta={'error': f'ScanTarget record not found ({scan_asset_id})'})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    asset = BaseTarget.objects.get(id=scan_asset.asset.id)

    # Iterate through the selected policies and fetch their rules
    policy_rules = []
    for policy in scan.policies.all():
        for rule in policy.current_version.rules.all():
            policy_rules.append((policy, rule))

    total_rules = len(policy_rules)
    rules_run = 0
    for policy, rule in policy_rules:
        logger.info('Starting rule evaluation', extra={'id': rule.id})

        if asset.REQUIRES_EMBEDDINGS:
            # template policies should not be bound to a user
            add_user_filter = not policy.is_template
            user = scan.user if add_user_filter else None
            embedding = create_embedding(rule.query_string, asset.embedding_model, asset.embedding_model_service, user)
            query = embedding.vectors
        else:
            query = rule.query_string
        results = asset.search(query, max_results=100)

        for text in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = Result(rule=rule, text=text, scan_asset=scan_asset)
            result.save()

            # Run the regex against the text
            for match in re.finditer(rule.regex_test, text):

                # Persist the finding
                finding = Finding(result=result, offset=match.start(), length=match.end() - match.start())
                finding.save()

        # Update the progress counter based on the number of rules that have been evaluated
        rules_run += 1
        scan_asset.progress = int(rules_run / total_rules * 100)
        scan_asset.save()

    # Persist the completion time of the scan
    scan_asset.finished_at = timezone.now()
    scan_asset.save()

    logger.info('Scan task complete', extra={'scan_asset_id': scan_asset.id})

    # If any of the scan assets are running, skip setting the main scan status to complete
    for scan_asset in scan.scan_assets.all():
        if scan_asset.finished_at is None:
            return

    scan.status = 'Complete'
    scan.finished_at = timezone.now()
    scan.save()

    logger.info('Scan complete', extra={'scan_id': scan.id})
