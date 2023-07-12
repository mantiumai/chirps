"""Celery tasks for the scan application."""
import json
import re
from logging import getLogger

from celery import shared_task
from django.utils import timezone
from embedding.utils import create_embedding
from target.providers.pinecone import PineconeTarget
from target.providers.redis import RedisTarget
from target.models import BaseTarget

from .models import Finding, Result, Scan

logger = getLogger(__name__)


@shared_task
def scan_task(scan_id):
    """Scan task."""
    logger.info('Starting scan', extra={'id': scan_id})

    try:
        scan = Scan.objects.get(pk=scan_id)
    except Scan.DoesNotExist:
        logger.error('Scan record not found', extra={'id': scan_id})

        scan_task.update_state(state='FAILURE', meta={'error': f'Scan record not found ({scan_id})'})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    target = BaseTarget.objects.get(id=scan.target.id)
    embed_query = isinstance(target, (RedisTarget, PineconeTarget))

    # Now that we have the derrived class, call its implementation of search()
    total_rules = scan.plan.rules.all().count()
    rules_run = 0
    for rule in scan.plan.rules.all():
        if embed_query:
            embedding = create_embedding(rule.query_string, 'text-embedding-ada-002', 'OA', scan.user)
            print(f'vectors: {embedding.vectors}')
            query = embedding.vectors
        else:
            query = rule.query_string
        logger.info('Starting rule evaluation', extra={'id': rule.id})
        results = target.search(query, max_results=100)

        for text in results:

            # Create the result. We'll flip the result flag to True if any findings are found
            result = Result(rule=rule, text=text, scan=scan)
            result.save()

            # Run the regex against the text
            for match in re.finditer(rule.regex_test, text):

                # Persist the finding
                finding = Finding(result=result, offset=match.start(), length=match.end() - match.start())
                finding.save()

        # Update the progress counter based on the number of rules that have been evaluated
        rules_run += 1
        scan.progress = int(rules_run / total_rules * 100)
        scan.save()

    # Persist the completion time of the scan
    scan.finished_at = timezone.now()
    scan.save()
    logger.info('Scan complete', extra={'id': scan_id})
