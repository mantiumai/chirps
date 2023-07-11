"""View handlers for targets."""
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import target_from_html_name, targets
from .models import BaseTarget
from .providers.pinecone import PineconeTarget


def decrypted_keys(request):
    """Return a list of decrypted API keys for all Pinecone targets."""
    keys = []
    for target in PineconeTarget.objects.all():
        keys.append(target.decrypted_api_key)
    return JsonResponse({'keys': keys})


@login_required
def dashboard(request):
    """Render the dashboard for the target app.

    Args:
        request (HttpRequest): Django request object
    """

    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_targets = BaseTarget.objects.filter(user=request.user).order_by('id')
    paginator = Paginator(user_targets, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_targets = BaseTarget.objects.filter(user=request.user)
    return render(request, 'target/dashboard.html', {'available_targets': targets, 'page_obj': page_obj})


@login_required
def create(request, html_name):
    """Render the create target form.

    Args:
        request (HttpRequest): Django request object
        html_name (str): used to get the target dictionary entry
    """
    if request.method == 'POST':

        # Get the target dictionary entry from the html_name parameter
        target = target_from_html_name(html_name=html_name)
        form = target['form'](request.POST)

        if form.is_valid():

            # Persist the
            form.user = request.user

            # Convert the form into a target object (don't persist to the DB yet)
            target = form.save(commit=False)

            # Assign the target to the current user
            target.user = request.user

            # Off to the DB we go!
            target.save()

            # Redirect the user back to the dashboard
            return redirect('target_dashboard')

    else:
        target = target_from_html_name(html_name=html_name)
        form = target['form']()

    return render(request, 'target/create.html', {'form': form, 'target': target})


@login_required
def delete(request, target_id):   # pylint: disable=unused-argument
    """Delete a target from the database."""
    get_object_or_404(BaseTarget, pk=target_id).delete()
    return redirect('target_dashboard')
