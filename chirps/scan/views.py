"""Views for the scan application."""
from collections import defaultdict

from asset.models import BaseAsset
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from embedding.models import Embedding
from policy.models import Policy

from .forms import ScanForm
from .models import Finding, Result, Scan, ScanAsset
from .tasks import scan_task


@login_required
def finding_detail(request, finding_id):
    """Render the finding detail page."""
    finding = get_object_or_404(Finding, pk=finding_id, result__scan__user=request.user)
    return render(request, 'scan/finding_detail.html', {'finding': finding})


@login_required
def result_detail(request, scan_id, policy_id, rule_id):
    """Render the scan result detail page."""
    scan = get_object_or_404(Scan, id=scan_id, user=request.user)
    results = Result.objects.filter(scan=scan, rule__id=rule_id, rule__policy__id=policy_id)
    if not results.exists():
        raise Http404('Results not found')

    findings = Finding.objects.filter(result__in=results)

    return render(request, 'scan/result_detail.html', {'results': results, 'findings': findings})


@login_required
def view_scan(request, scan_id):
    """View details for a particular scan."""
    scan = get_object_or_404(Scan, pk=scan_id, user=request.user)

    # Assemble a slit of all the results that had findings, across all assets
    results = []
    scan_assets = ScanAsset.objects.filter(scan=scan)

    # Step 1: build a list of all the results (rules) with findings.
    for scan_asset in scan_assets:
        # Iterate through the rule set
        for result in scan_asset.results.all():
            if result.has_findings():
                results.append(result)

    # Step 2: aggregate results by rules with matching rule IDs
    unique_rules = {result.rule for result in results}

    # Next, walk through all of the results, aggregating the findings count for each unique rule ID
    finding_count = 0
    finding_severities = defaultdict(int)

    # Walk through each unique rule
    for rule in unique_rules:
        rule.finding_count = 0
        rule.findings = []

        # Iterate through each result that was hit for the rule
        for result in results:

            # Increment the number of findings for this rule
            if result.rule.id == rule.id:
                findings = list(result.findings.all())
                count = len(findings)
                rule.finding_count += count
                finding_count += count
                rule.findings.extend(findings)

                # While we're in this loop, store off the number of times each severity is encountered
                # This will be used to render the pie-chart in the UI
                finding_severities[rule.severity] += count

    return render(
        request,
        'scan/scan.html',
        {
            'scan': scan,  # The scan object
            'finding_count': finding_count,  # Total number of findings
            'unique_rules': unique_rules,  # List of unique rules hit by findings
            'severities': list(finding_severities.keys()),  # List of all the severities encountered
            'severity_counts': list(finding_severities.values()),  # List of all the severity counts encountered
        },
    )


@login_required
def create(request):
    """Render the scan creation page and handle POST requests."""
    if request.method == 'POST':
        scan_form = ScanForm(request.POST, user=request.user)
        scan_form.full_clean()

        if scan_form.is_valid():
            # Set the selected policies to the scan
            selected_policies = scan_form.cleaned_data['policies']
            # Check if the user has configured their OpenAI key
            policies_and_rules = [
                (policy, rule) for policy in selected_policies for rule in policy.current_version.rules.all()
            ]
            if any(
                not policy.is_template and not Embedding.objects.filter(text=rule.query_string).exists()
                for policy, rule in policies_and_rules
            ):
                if not request.user.profile.openai_key:
                    messages.error(request, 'User has not configured their OpenAI key')
                    return redirect('scan_create')

            # Convert the scan form into a scan model
            scan = scan_form.save(commit=False)

            # Assign the scan to a user
            scan.user = request.user

            # Persist the scan to the database without committing the many-to-many relationship
            scan.save()

            scan_form.save_m2m()

            scan.policies.set(selected_policies)

            # For every asset that was selected, kick off a task
            for asset in scan_form.cleaned_data['assets']:
                scan_asset = ScanAsset.objects.create(scan=scan, asset=asset)

                # Kick off the scan task
                result = scan_task.delay(scan_asset_id=scan_asset.id)

                # Save off the Celery task ID on the Scan object
                scan_asset.celery_task_id = result.id
                scan_asset.save()

            # Redirect the user back to the dashboard
            return redirect('scan_dashboard')

    else:
        scan_form = ScanForm()

    # Fetch the list of template and custom policies
    templates = Policy.objects.filter(is_template=True).order_by('id')
    user_policies = Policy.objects.filter(user=request.user, archived=False, is_template=False).order_by('id')
    assets = BaseAsset.objects.filter(user=request.user)

    return render(
        request,
        'scan/create.html',
        {'form': scan_form, 'user_policies': user_policies, 'templates': templates, 'assets': assets},
    )


@login_required
def dashboard(request):
    """Render the scan dashboard."""
    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_scans = Scan.objects.filter(user=request.user).order_by('started_at')
    paginator = Paginator(user_scans, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scan/dashboard.html', {'page_obj': page_obj})


@login_required
def status(request, scan_id):
    """Fetch the status of a scan job."""
    scan = get_object_or_404(Scan, pk=scan_id, user=request.user)

    # Respond with the status of the celery task and the progress percentage of the scan
    response = f'{scan.status} : {scan.progress()} %'

    if scan.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=response, status=286)

    # Walk through all of the ScanAsset entries (tasks)
    # If none of them are running anymore, something has gone wrong!
    for scan_asset in scan.scan_assets.all():
        if scan_asset.finished_at is None:
            return HttpResponse(content=response, status=200)
    return HttpResponse(content=response, status=200)


@login_required
def asset_status(request, scan_asset_id):
    """Fetch the status of a scan job."""
    scan_asset = get_object_or_404(ScanAsset, pk=scan_asset_id, scan__user=request.user)

    template = loader.get_template('scan/asset_status.html')

    celery_status = scan_asset.celery_task_status()
    rendered_template = template.render({'scan_asset': scan_asset, 'celery_status': celery_status}, request)

    if scan_asset.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=rendered_template, status=286)

    return HttpResponse(content=rendered_template, status=200)


@login_required
def findings_count(request, scan_id):
    """Fetch the number of findings associated with a scan."""
    scan = get_object_or_404(Scan, pk=scan_id, user=request.user)

    # Respond with the status of the celery task and the progress percentage of the scan
    response = scan.findings_count()

    if scan.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=response, status=286)

    return HttpResponse(content=response, status=200)
