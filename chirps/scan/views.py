"""Views for the scan application."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from policy.models import Policy
from target.models import BaseTarget

from .forms import ScanForm
from .models import Finding, Result, Scan
from .tasks import scan_task


@login_required
def finding_detail(request, finding_id):
    """Render the finding detail page."""
    finding = get_object_or_404(Finding, pk=finding_id, result__scan__user=request.user)
    return render(request, 'scan/finding_detail.html', {'finding': finding})


@login_required
def result_detail(request, result_id):
    """Render the scan result detail page."""
    result = get_object_or_404(Result, pk=result_id, scan__user=request.user)
    return render(request, 'scan/result_detail.html', {'result': result})


@login_required
def create(request):
    """Render the scan creation page and handle POST requests."""
    if request.method == 'POST':
        scan_form = ScanForm(request.POST)
        if scan_form.is_valid():

            # Convert the scan form into a scan model
            scan = scan_form.save(commit=False)

            # Assign the scan to a user
            scan.user = request.user

            # Persist the scan to the database without committing the many-to-many relationship
            scan.save()

            scan_form.save_m2m()

            # Set the selected policies to the scan
            selected_policies = scan_form.cleaned_data['policies']
            scan.policies.set(selected_policies)

            # Kick off the scan task
            result = scan_task.delay(scan.id)

            # Save off the Celery task ID on the Scan object
            scan.celery_task_id = result.id
            scan.save()

            # Redirect the user back to the dashboard
            return redirect('scan_dashboard')

    else:
        scan_form = ScanForm()

    # Fetch the list of template and custom policies
    templates = Policy.objects.filter(is_template=True).order_by('id')
    user_policies = Policy.objects.filter(user=request.user, archived=False, is_template=False).order_by('id')
    targets = BaseTarget.objects.filter(user=request.user)

    return render(
        request,
        'scan/create.html',
        {'form': scan_form, 'user_policies': user_policies, 'templates': templates, 'targets': targets},
    )


@login_required
def dashboard(request):
    """Render the scan dashboard."""
    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_scans = Scan.objects.filter(user=request.user).order_by('started_at')
    paginator = Paginator(user_scans, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # We're going to perform some manual aggregation (sqlite doesn't support calls to distinct())
    for scan in page_obj:
        scan.policy_results = {}

        for result in scan.result_set.all():
            policy = result.rule.policy
            if policy not in scan.policy_results:
                scan.policy_results[policy] = {}

            if result.rule not in scan.policy_results[policy]:
                scan.policy_results[policy][result.rule] = {
                    'id': result.id,
                    'rule': result.rule,
                    'findings': 0,
                }

            scan.policy_results[policy][result.rule]['findings'] += result.finding_set.count()

    return render(request, 'scan/dashboard.html', {'page_obj': page_obj})


@login_required
def status(request, scan_id):
    """Fetch the status of a scan job."""
    scan = get_object_or_404(Scan, pk=scan_id, user=request.user)

    # Respond with the status of the celery task and the progress percentage of the scan
    response = f'{scan.celery_task_status()} : {scan.progress} %'

    if scan.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=response, status=286)

    return HttpResponse(content=response, status=200)
