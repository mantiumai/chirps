"""Severity views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from severity.forms import CreateSeverityForm, EditSeverityForm
from severity.models import Severity


def is_superuser(user: User) -> bool:
    """Check if the user is a superuser."""
    return user.is_superuser


@user_passes_test(is_superuser)     # type: ignore
@login_required
def create_severity(request: HttpRequest) -> HttpResponse:
    """Create a new severity."""
    if request.method == 'POST':
        form = CreateSeverityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Severity created successfully.')
        else:
            messages.error(request, 'Error creating severity.')
        return redirect('policy_dashboard')

    return HttpResponseNotAllowed(['POST'])


@user_passes_test(is_superuser)     # type: ignore
@login_required
def edit_severity(request: HttpRequest, severity_id: int) -> HttpResponse:
    """Edit an existing severity."""
    severity = get_object_or_404(Severity, id=severity_id)
    if request.method == 'POST':
        form = EditSeverityForm(request.POST, instance=severity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Severity updated successfully.')
        else:
            messages.error(request, 'Error updating severity.')
        return redirect('policy_dashboard')

    return HttpResponseNotAllowed(['POST'])


@user_passes_test(is_superuser)     # type: ignore
@login_required
def archive_severity(request: HttpRequest, severity_id: int) -> HttpResponse:
    """Archive a severity."""
    try:
        severity = Severity.objects.get(id=severity_id)
        severity.archived = True
        severity.save()
        messages.success(request, f"Severity '{severity.name}' has been archived.")
    except Severity.DoesNotExist:
        messages.error(request, 'Severity not found.')

    return redirect('policy_dashboard')
