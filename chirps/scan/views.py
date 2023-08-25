"""Views for the scan application."""
from collections import defaultdict
from logging import getLogger

from asset.models import BaseAsset
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils import timezone
from embedding.models import Embedding
from policy.models import Policy

from chirps.celery import app as celery_app

from .forms import ScanForm
from .models import BaseFinding, ScanAsset, ScanRun, ScanTemplate, ScanVersion
from .tasks import scan_task

logger = getLogger(__name__)


@login_required
def finding_detail(request, finding_id):
    """Render the finding detail page."""
    finding = get_object_or_404(BaseFinding, pk=finding_id, result__scan__user=request.user)
    return render(request, 'scan/finding_detail.html', {'finding': finding})


@login_required
def view_scan_history(request, scan_id):
    """View the history of a particular scan."""
    scan = get_object_or_404(ScanTemplate, pk=scan_id, user=request.user)
    scan_runs = ScanRun.objects.filter(scan_version__scan=scan).order_by('-id')

    # Paginate the number of items returned to the user, defaulting to 25 per page
    paginator = Paginator(scan_runs, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'scan/scan_history.html',
        {
            'scan': scan,  # The scan object
            'paginator': paginator,  # Paginator object
            'page_obj': page_obj,  # List of scan versions
        },
    )


@login_required
def view_scan_run(request, scan_run_id):
    """View details for a particular scan."""
    scan_run = get_object_or_404(ScanRun, pk=scan_run_id, scan_version__scan__user=request.user)

    # Assemble a list of all the results that had findings, across all assets
    results = []
    scan_assets = ScanAsset.objects.filter(scan=scan_run)

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

    # Retrieve finding_preview_size from the user's profile
    finding_preview_size = request.user.profile.finding_preview_size

    return render(
        request,
        'scan/scan_run.html',
        {
            'scan_run': scan_run,  # The scan run object
            'finding_count': finding_count,  # Total number of findings
            'unique_rules': unique_rules,  # List of unique rules hit by findings
            'severities': list(finding_severities.keys()),  # List of all the severities encountered
            'severity_counts': list(finding_severities.values()),  # List of all the severity counts encountered
            'finding_preview_size': finding_preview_size,
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

            # Check if the scan requires an OpenAI key
            policies_and_rules = []

            for policy in selected_policies:
                for rule in policy.current_version.rules.all():
                    policies_and_rules.append((policy, rule))

            # Check if any non-template policies don't have an associated embedding for their rule's query_string
            rule_strings = [rule.query_string for policy, rule in policies_and_rules if not policy.is_template]
            rule_count = len(rule_strings)

            rule_embedding_count = Embedding.objects.filter(text__in=rule_strings).count()
            missing_embeddings = rule_embedding_count != rule_count

            selected_assets = scan_form.cleaned_data['assets']
            # an API key is required to generate embeddings if any are missing
            fail_scan_create = False
            for asset in selected_assets:
                if missing_embeddings and hasattr(asset, 'embedding_model_service'):
                    if (
                        asset.embedding_model_service == Embedding.Service.OPEN_AI
                        and not request.user.profile.openai_key
                    ):
                        fail_scan_create = True
                        messages.error(request, 'User has not configured their OpenAI API key')
                    elif (
                        asset.embedding_model_service == Embedding.Service.COHERE
                        and not request.user.profile.cohere_key
                    ):
                        fail_scan_create = True
                        messages.error(request, 'User has not configured their cohere API key')

            if fail_scan_create is True:
                return redirect('scan_create')

            # Convert the scan form into a scan model
            # Create the initial Scan model
            new_scan = ScanTemplate.objects.create(
                name=scan_form.cleaned_data['name'],
                description=scan_form.cleaned_data['description'],
                user=request.user,
            )
            # Create the initial ScanVersion model
            new_scan_version = ScanVersion.objects.create(
                scan=new_scan,
            )

            # Set the foreign keys to the selected policies and assets
            new_scan_version.policies.set(selected_policies)
            new_scan_version.assets.set(selected_assets)
            new_scan_version.save()

            # Set the initial version in the Scan model
            new_scan.current_version = new_scan_version
            new_scan.save()

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
def edit(request, scan_id):
    """Render the scan edit page and handle POST requests."""
    scan = get_object_or_404(ScanTemplate, pk=scan_id, user=request.user)

    if request.method == 'POST':
        scan_form = ScanForm(request.POST, user=request.user, instance=scan)
        scan_form.full_clean()

        if scan_form.is_valid():
            # Set the selected policies to the scan
            selected_policies = scan_form.cleaned_data['policies']

            # Check if the scan requires an OpenAI key
            policies_and_rules = []

            for policy in selected_policies:
                for rule in policy.current_version.rules.all():
                    policies_and_rules.append((policy, rule))

            # Check if any non-template policies don't have an associated embedding for their rule's query_string
            rule_strings = [rule.query_string for policy, rule in policies_and_rules if not policy.is_template]
            rule_count = len(rule_strings)

            rule_embedding_count = Embedding.objects.filter(text__in=rule_strings).count()
            missing_embeddings = rule_embedding_count != rule_count

            selected_assets = scan_form.cleaned_data['assets']
            # an API key is required to generate embeddings if any are missing
            fail_scan_create = False
            for asset in selected_assets:
                if missing_embeddings and hasattr(asset, 'embedding_model_service'):
                    if (
                        asset.embedding_model_service == Embedding.Service.OPEN_AI
                        and not request.user.profile.openai_key
                    ):
                        fail_scan_create = True
                        messages.error(request, 'User has not configured their OpenAI API key')
                    elif (
                        asset.embedding_model_service == Embedding.Service.COHERE
                        and not request.user.profile.cohere_key
                    ):
                        fail_scan_create = True
                        messages.error(request, 'User has not configured their cohere API key')

            if fail_scan_create is True:
                return redirect('scan_edit', scan_id=scan.id)

            # Update the top level scan fields, if they've changed
            scan.description = scan_form.cleaned_data['description']
            scan.name = scan_form.cleaned_data['name']
            scan.save()

            # Create the new ScanVersion model
            new_scan_version = ScanVersion.objects.create(scan=scan, number=scan.current_version.number + 1)

            # Set the foreign keys to the selected policies and assets
            new_scan_version.policies.set(selected_policies)
            new_scan_version.assets.set(selected_assets)
            new_scan_version.save()

            # Set the initial version in the Scan model
            scan.current_version = new_scan_version
            scan.save()

            # Redirect the user back to the dashboard
            return redirect('scan_dashboard')

    else:
        scan_form = ScanForm().from_scan(scan)

    selected_policies = [policy.id for policy in scan.policies()]
    selected_assets = [asset.id for asset in scan.assets()]

    # Fetch the list of template and custom policies
    templates = Policy.objects.filter(is_template=True).order_by('id')
    user_policies = Policy.objects.filter(
        Q(user=request.user, archived=False, is_template=False) | Q(is_template=True, archived=False)
    ).order_by('id')
    assets = BaseAsset.objects.filter(user=request.user)

    return render(
        request,
        'scan/edit.html',
        {
            'form': scan_form,
            'user_policies': user_policies,
            'templates': templates,
            'assets': assets,
            'scan': scan,
            'selected_assets': selected_assets,
            'selected_policies': selected_policies,
        },
    )


@login_required
def dashboard(request):
    """Render the scan dashboard."""
    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_scans = ScanTemplate.objects.filter(user=request.user).order_by('id')
    paginator = Paginator(user_scans, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scan/dashboard.html', {'page_obj': page_obj})


@login_required
def status(request, scan_run_id):
    """Fetch the status of a scan job."""
    scan = get_object_or_404(ScanRun, pk=scan_run_id, scan_version__scan__user=request.user)

    # Respond with the status of the celery task and the progress percentage of the scan
    response = f'{scan.status} : {scan.progress()} %'

    if scan.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=response, status=286)

    # Walk through all of the ScanAsset entries (tasks)
    # If none of them are running anymore, something has gone wrong!
    for scan_asset in scan.scan_run_assets.all():
        if scan_asset.finished_at is None:
            return HttpResponse(content=response, status=200)
    return HttpResponse(content=response, status=200)


@login_required
def asset_status(request, scan_asset_id):
    """Fetch the status of a scan job."""
    scan_asset = get_object_or_404(ScanAsset, pk=scan_asset_id, scan__scan_version__scan__user=request.user)

    template = loader.get_template('scan/asset_status.html')

    celery_status = scan_asset.celery_task_status()
    rendered_template = template.render({'scan_asset': scan_asset, 'celery_status': celery_status}, request)

    if scan_asset.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=rendered_template, status=286)

    return HttpResponse(content=rendered_template, status=200)


@login_required
def findings_count(request, scan_run_id):
    """Fetch the number of findings associated with a scan run."""
    scan_run = get_object_or_404(ScanRun, pk=scan_run_id, scan_version__scan__user=request.user)

    # Respond with the status of the celery task and the progress percentage of the scan
    response = scan_run.findings_count()

    if scan_run.finished_at is not None:
        # HTMX will stop polling if we return a 286
        return HttpResponse(content=response, status=286)

    return HttpResponse(content=response, status=200)


@login_required
def vcr_control(request, scan_id):
    """Render the VCR control, based on if any scans are running."""
    scan = get_object_or_404(ScanTemplate, pk=scan_id, user=request.user)
    return render(request, 'scan/vcr.html', {'scan': scan})


@login_required
def vcr_start(request, scan_id):
    """Kick off a scan job from the VCR controls, returning a new set of controls."""
    scan = get_object_or_404(ScanTemplate, pk=scan_id, user=request.user)

    # Something was out of sync, redirect the user back to the scan history view
    if scan.is_running():
        messages.error(request, 'Scan is already running')
        return redirect('scan_history_view', scan_id=scan.id)

    # Create a new scan run
    scan_run = ScanRun.objects.create(
        scan_version=scan.current_version,
    )

    # For every asset configured for the scan, kick off a task
    for asset in scan.assets():
        scan_asset = ScanAsset.objects.create(scan=scan_run, asset=asset)

        # Kick off the scan task
        result = scan_task.delay(scan_asset_id=scan_asset.id)

        # Save off the Celery task ID on the Scan object
        scan_asset.celery_task_id = result.id
        scan_asset.save()

    # Refresh the scan object before handing it off to the template
    scan.refresh_from_db()

    return render(request, 'scan/vcr.html', {'scan': scan})


@login_required
def vcr_stop(request, scan_id):   # pylint: disable=unused-argument
    """Stop or cancel a job that is currently running (or queued)."""
    scan = get_object_or_404(ScanTemplate, pk=scan_id, user=request.user)

    if scan.is_running():

        # Grab the running scan
        scan_run = ScanRun.objects.get(scan_version__scan=scan, status__in=['Running', 'Queued'])

        # Each asset that is part of the scan has a task associated with it
        # Walk through each available task and cancel it using Celery job control

        for scan_asset in scan_run.run_assets.all():

            print(f'Processing scan asset {scan_asset.id}')
            if scan_asset.celery_task_id is not None:
                celery_app.control.revoke(scan_asset.celery_task_id, terminate=True)
                print(f'Terminated Celery task {scan_asset.celery_task_id}')

            scan_asset.finished_at = timezone.now()
            scan_asset.save()

        scan_run.status = 'Canceled'
        scan_run.finished_at = timezone.now()
        scan_run.save()

    # Return the VCR controls
    return render(request, 'scan/vcr.html', {'scan': scan})
