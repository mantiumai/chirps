"""Views for the plan app."""
from django.shortcuts import render

from .models import Plan


def dashboard(request):
    """Render the dashboard for the plan app.

    Args:
        request (HttpRequest): Django request object
    """

    # Fetch a list of all the available template plans
    templates = Plan.objects.filter(is_template=True)

    return render(request, 'plan/dashboard.html', {'templates': templates})


def create(request):
    """Render the create plan form.

    Args:
        request (HttpRequest): Django request object
    """
    # Fetch a list of all the available template plans
    return render(request, 'plan/create.html', {})
