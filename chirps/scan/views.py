import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404

from .forms import ScanForm
from .models import Result, Scan, Finding
from .tasks import scan_task

@login_required
def finding_detail(request, finding_id):
    finding = get_object_or_404(Finding, pk=finding_id, result__scan__user=request.user)
    return render(request, 'scan/finding_detail.html', {'finding': finding})

@login_required
def result_detail(request, result_id):
    result = get_object_or_404(Result, pk=result_id, scan__user=request.user)
    return render(request, 'scan/result_detail.html', {'result': result})

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
    # TODO: Add pagination
    user_scans = Scan.objects.filter(user=request.user)

    # We're going to perform some manual aggregation (sqlite doesn't support calls to distinct())
    for scan in user_scans:

        scan.rules = {}

        for result in scan.result_set.all():
            if result.rule.name not in scan.rules:
                scan.rules[result.rule.name] = {'id': result.id, 'rule': result.rule, 'findings': Finding.objects.filter(result=result).count()}

        # Convert the dictionary into a list that the template can iterate on
        scan.rules = scan.rules.values()

    return render(request, 'scan/dashboard.html', {'scans': user_scans})
