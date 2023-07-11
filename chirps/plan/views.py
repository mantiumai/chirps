"""Views for the plan app."""
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Plan


def dashboard(request):
    """Render the dashboard for the plan app.

    Args:
        request (HttpRequest): Django request object
    """
    # Fetch a list of all the available template plans

    # Paginate the number of items returned to the user, defaulting to 25 per page
    templates = Plan.objects.filter(is_template=True).order_by('id')
    paginator = Paginator(templates, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    templates = Plan.objects.filter(is_template=True)

    return render(request, 'plan/dashboard.html', {'page_obj': page_obj})


def create(request):
    """Render the create plan form.

    Args:
        request (HttpRequest): Django request object
    """
    # Fetch a list of all the available template plans
    return render(request, 'plan/create.html', {})
