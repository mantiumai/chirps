"""Celery tasks for the scan application."""
import re
from logging import getLogger

from asset.models import BaseAsset, SearchResult
from celery import shared_task
from django.utils import timezone
from embedding.utils import create_embedding

from .models import Finding, Result, ScanAsset, ScanAssetFailure

logger = getLogger(__name__)


# pylint: disable=unused-argument,too-many-arguments
def task_failure_handler(self, exc, task_id, args, kwargs, einfo):
    """
    Create task ScanAssetFailure record when a task fails.

    exc (Exception) - The exception raised by the task.
    task_id (str) - Unique id of the failed task.
    args (Tuple) - Original arguments for the task that failed.
    kwargs (Dict) - Original keyword arguments for the task that failed.
    einfo (ExceptionInfo) - Exception information.
    """
    logger.error('Scan task failed', extra={'exc': exc, 'einfo': einfo, 'task_id': task_id})

    # Fetch the ScanAsset that this failure belongs to
    scan_asset = ScanAsset.objects.get(celery_task_id=task_id)
    scan_asset.finished_at = timezone.now()
    scan_asset.save()

    ScanAssetFailure.objects.create(scan_asset=scan_asset, exception=str(exc), traceback=str(einfo))

    # If any of the other scan assets are running, skip setting the main scan status to complete
    scan = scan_asset.scan
    for scan_asset in scan.scan_assets.all():
        if scan_asset.finished_at is None:
            return

    # All of the other scan assets are complete, so we can mark the scan as failed
    scan.status = 'Failed'
    scan.finished_at = timezone.now()
    scan.save()


@shared_task(on_failure=task_failure_handler)
def scan_task(scan_asset_id):
    """Scan task."""
    logger.info('Starting scan task', extra={'scan_asset_id': scan_asset_id})

    try:
        scan_asset = ScanAsset.objects.get(pk=scan_asset_id)
        scan = scan_asset.scan

        # Update scan status
        scan.status = 'Running'
        scan.save()

    except ScanAsset.DoesNotExist:
        logger.error('ScanAsset record not found', extra={'scan_asset_id': scan_asset_id})
        scan_task.update_state(state='FAILURE', meta={'error': f'ScanAsset record not found ({scan_asset_id})'})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    asset = BaseAsset.objects.get(id=scan_asset.asset.id)

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

        # Issue the search query to the asset provider
        results: list[SearchResult] = asset.search(query, max_results=100)

        for search_result in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = Result(rule=rule, text=search_result.data, scan_asset=scan_asset)
            result.save()

            # Run the regex against the text
            for match in re.finditer(rule.regex_test, search_result.data):

                # Persist the finding
                finding = Finding(
                    result=result,
                    offset=match.start(),
                    length=match.end() - match.start(),
                    source_id=search_result.source_id,
                )
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

    # Double check to see if any of the scan assets failed
    for scan_asset in scan.scan_assets.all():
        if scan_asset.celery_task_status() == 'FAILURE':
            scan.status = 'Failed'
            scan.finished_at = timezone.now()
            scan.save()
            return

    # Everything went well, mark the scan as complete!
    scan.status = 'Complete'
    scan.finished_at = timezone.now()
    scan.save()

    logger.info('Scan complete', extra={'scan_id': scan.id})
