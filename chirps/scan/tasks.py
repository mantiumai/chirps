import re
import json
import logging
from celery import shared_task
from django.utils import timezone
from target.models import BaseTarget

from .models import Result, Rule, Scan

logger = logging.getLogger(__name__)  

@shared_task
def add(x, y):
    return x + y


@shared_task
def scan_task(scan_id):
    print("scan_task started")

    print(f'Running a scan {scan_id}')
    try:
        scan = Scan.objects.get(pk=scan_id)
    except Scan.DoesNotExist:
        error = f'Scan {scan_id} does not exist'
        print(error)
        scan_task.update_state(state='FAILURE', meta={'error': error})
        return

    # Need to perform a secondary query in order to fetch the derrived class
    # This magic is handled by django-polymorphic
    target = BaseTarget.objects.get(id=scan.target.id)

    # Now that we have the derrived class, call its implementation of search()
    for rule in scan.plan.rules.all():
        print(f'Running rule {rule}')
        results = target.search(query=rule.query_string, max_results=100)

        matches = 0
        for text in results:
            matches += len(re.findall(rule.regex_test, text))

        # Perform the regex against the results
        # TODO: Convert the query to an embedding if required by the target.

        details = {}  # Create a dictionary to store the details  
  
        for index, text in enumerate(results):  
            matches_in_text = re.findall(rule.regex_test, text)  
            matches += len(matches_in_text)  
            
            details[f"result_{index + 1}"] = {  
                "text": text,  
                "matches": matches_in_text,  
            }  
        
        logger.debug('Details dictionary: %s', details)
        
        details_json = json.dumps(details)  
        logger.debug('Details JSON: %s', details_json)
        result = Result(count=matches, result=True, rule=rule, details=details_json)  

        result.save()  
        logger.debug('Saved result with details: %s', result.details)
        
        scan.results.add(result)  

    
    # Persist the completion time of the scan
    scan.finished_at = timezone.now()
    scan.save()
    print(f'Saved scan results')
