import re
from celery import shared_task
from django.utils import timezone
from target.models import BaseTarget

from .models import Scan


@shared_task
def add(x, y):
    return x + y


@shared_task
def scan_task(scan_id):

    print(f'Running a scan {scan_id}')
    try:
        scan = Scan.objects.get(pk=scan_id)
    except Scan.DoesNotExist:
        error = f'Scan {scan_id} does not exist'
        print(error)
        scan_task.update_state(state='FAILURE', meta={'error': error})
        return

    target = scan.target

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    target = BaseTarget.objects.get(id=scan.target.id)

    # Now that we have the derrived class, call its implementation of search()
    for rule in scan.plan.rules.all():
        print(f'Running rule {rule}')
        results = target.search(query=rule.query_string, max_results=100)

        print(results)

        matches = []
        for text in results:
            matches.extend(re.findall(rule.regex_test, text))

        print(matches)

        # Perform the regex against the results
        # TODO: Convert the query to an embedding if required by the target.

    # result = target.search(query=search_prompt, max_results=100)
    # print(result)

    # Persist the completion time of the scan
    scan.finished_at = timezone.now()
    scan.save()
    print(f'Saved scan results')
