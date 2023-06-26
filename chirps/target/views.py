"""View handlers for targets."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import target_from_html_name, targets
from .models import BaseTarget


@login_required
def dashboard(request):
    """Render the dashboard for the target app.

    Args:
        request (HttpRequest): Django request object
    """
    return render(
        request, 'target/dashboard.html', {'available_targets': targets, 'user_targets': BaseTarget.objects.all()}
    )


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

            # Save the form to the database
            form.save()

            # Redirect the user back to the dashboard
            return redirect('target_dashboard')

    else:
        target = target_from_html_name(html_name=html_name)
        form = target['form']()

    return render(request, 'target/create.html', {'form': form, 'target': target})


@login_required
def delete(request, target_id):
    """Delete a target from the database."""
    get_object_or_404(BaseTarget, pk=target_id).delete()
    return redirect('target_dashboard')
