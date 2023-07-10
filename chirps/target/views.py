"""View handlers for targets."""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from redis import exceptions

from .forms import target_from_html_name, targets
from .models import BaseTarget
from .providers.pinecone import PineconeTarget
from .providers.redis import RedisTarget


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
    user_targets = BaseTarget.objects.filter(user=request.user)
    return render(request, 'target/dashboard.html', {'available_targets': targets, 'user_targets': user_targets})


@login_required
def create(request, html_name):
    """Render the create target form.

    Args:
        request (HttpRequest): Django request object
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
def ping(request, target_id):  
    """Ping a RedisTarget database using the test_connection() function."""  
    target = get_object_or_404(BaseTarget, pk=target_id)  
    if isinstance(target, RedisTarget):  
        try:
            result = target.test_connection()
            return JsonResponse({'success': result})
        except exceptions.ConnectionError:
            return JsonResponse({'success': False, 'error': 'Unable to connect to Redis'})
    return JsonResponse({'success': False, 'error': 'Not a RedisTarget'})



@login_required
def delete(request, target_id):   # pylint: disable=unused-argument
    """Delete a target from the database."""
    get_object_or_404(BaseTarget, pk=target_id).delete()
    return redirect('target_dashboard')
