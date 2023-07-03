import json  
import logging  
from django.contrib.auth.decorators import login_required  
from django.shortcuts import redirect, render, get_object_or_404  
from django.http import HttpResponseNotFound  
from .forms import ScanForm  
from .models import Scan, Result  
from .tasks import scan_task  
  
logger = logging.getLogger(__name__)  
  
@login_required  
def create(request):  
    if request.method == 'POST':  
        scan_form = ScanForm(request.POST)  
        if scan_form.is_valid():  
            # Convert the scan form into a scan model  
            scan = scan_form.save(commit=False)  
            # Assign the scan to a user  
            scan.user = request.user  
            # Persist the scan to the database  
            scan.save()  
            # Kick off the scan task  
            result = scan_task.delay(scan.id)  
            print("scan_task called")  
            # Save off the Celery task ID on the Scan object  
            scan.celery_task_id = result.id  
            scan.save()  
            # Redirect the user back to the dashboard  
            return redirect('scan_dashboard')  
    else:  
        scan_form = ScanForm()  
    return render(request, 'scan/create.html', {'scan_form': scan_form})  
  
@login_required  
def dashboard(request):  
    scans = Scan.objects.filter(user=request.user)  
    findings_count_lists = []  
  
    for scan in scans:  
        findings_count_list = []  
        for result in scan.results.all():  
            if result.details:  
                details = json.loads(result.details)  
                findings_count = sum([1 for key, value in details.items() if value['matches']])  
                findings_count_list.append((result, findings_count))  
            else:  
                findings_count_list.append((result, 0))  
        findings_count_lists.append(findings_count_list)  
  
    scan_data = zip(scans, findings_count_lists)  
    return render(request, 'scan/dashboard.html', {'scan_data': scan_data})  

  
@login_required  
def result_details(request, result_id):  
    result = get_object_or_404(Result, pk=result_id)  
    logger.debug('Result details: %s', result.details)  
    print('Result details:', result.details)  
  
    if result.details is None:  
        return HttpResponseNotFound("Details not found for this result.")  
  
    details = json.loads(result.details)  
    # Create a new list containing only the results with matches  
    filtered_details = []  
    for key, value in details.items():  
        if value['matches']:  
            filtered_details.append(value)  
  
    return render(request, 'scan/result_details.html', {'details': filtered_details})  
