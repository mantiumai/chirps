"""Celery tasks for the scan application."""
from logging import getLogger

from asset.models import BaseAsset
from celery import shared_task
from django.utils import timezone
from policy.models import RuleExecuteArgs

from .models import ScanAsset, ScanAssetFailure, ScanRun

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
    scan_run = scan_asset.scan
    for scan_asset in scan_run.run_assets.all():
        if scan_asset.finished_at is None:
            return

    # All of the other scan assets are complete, so we can mark the scan as failed
    scan_run.status = 'Failed'
    scan_run.finished_at = timezone.now()
    scan_run.save()


@shared_task(on_failure=task_failure_handler)
def one_shot_scan(scan_run_id):
    """Task for running a one-shot scan."""
    logger.info('Starting one shot scan task', extra={'scan_run_id': scan_run_id})
    try:
        scan_run = ScanRun.objects.get(pk=scan_run_id)

    except ScanRun.DoesNotExist:
        logger.error('ScanRun record not found', extra={'scan_run_id': scan_run_id})
        scan_task.update_state(state='FAILURE', meta={'error': f'ScanRun record not found ({scan_run_id})'})
        return

    # Test if the scan is running - mark it as failed if it is
    if scan_run.scan_version.scan.is_running():
        logger.info('Scan already running', extra={'scan_run_id': scan_run_id})
        scan_run.status = 'Skipped'
        scan_run.finished_at = timezone.now()
        scan_run.save()
        return

    # Kick off the scan run, which queues a scan task for each asset
    for asset in scan_run.scan_version.scan.assets():
        scan_asset = ScanAsset.objects.create(scan=scan_run, asset=asset)

        # Kick off the scan task
        result = scan_task.delay(scan_asset_id=scan_asset.id)

        # Save off the Celery task ID on the Scan object
        scan_asset.celery_task_id = result.id
        scan_asset.save()


@shared_task(on_failure=task_failure_handler)
def scan_task(scan_asset_id):
    """Execute policies against a single asset"""
    logger.info('Starting scan task', extra={'scan_asset_id': scan_asset_id})

    try:
        scan_asset = ScanAsset.objects.get(pk=scan_asset_id)
        scan_run = scan_asset.scan

        # Update scan status
        scan_run.status = 'Running'
        scan_run.save()

    except ScanAsset.DoesNotExist:
        logger.error('ScanAsset record not found', extra={'scan_asset_id': scan_asset_id})
        scan_task.update_state(state='FAILURE', meta={'error': f'ScanAsset record not found ({scan_asset_id})'})
        return

    # Need to perform a secondary query in order to fetch the derived class
    # This magic is handled by django-polymorphic
    asset = BaseAsset.objects.get(id=scan_asset.asset.id)

    # Build a complete list of all the rules, across policies, that need to be evaluated
    policy_rules = []
    for policy in scan_run.scan_version.policies.all():
        for rule in policy.current_version.rules.all():
            policy_rules.append((policy, rule))

    rules_run = 0
    total_rules = len(policy_rules)

    # Walk through the list of rules and evaluate them
    for policy, rule in policy_rules:

        rule.execute(RuleExecuteArgs(scan_asset=scan_asset, asset=asset))

        # Update the progress counter based on the number of rules that have been evaluated
        rules_run += 1
        scan_asset.progress = int(rules_run / total_rules * 100)
        scan_asset.save()

    # Persist the completion time of the scan
    scan_asset.finished_at = timezone.now()
    scan_asset.save()

    logger.info('Scan task complete', extra={'scan_asset_id': scan_asset.id})

    # If any of the scan assets are running, skip setting the main scan status to complete
    for scan_asset in scan_run.run_assets.all():
        if scan_asset.finished_at is None:
            return

    # Double check to see if any of the scan assets failed
    for scan_asset in scan_run.run_assets.all():
        if scan_asset.celery_task_status() == 'FAILURE':
            scan_run.status = 'Failed'
            scan_run.finished_at = timezone.now()
            scan_run.save()
            return

    # Everything went well, mark the entire scan run as complete!
    scan_run.status = 'Complete'
    scan_run.finished_at = timezone.now()
    scan_run.save()

    logger.info('Scan complete', extra={'scan_id': scan_asset.id})
