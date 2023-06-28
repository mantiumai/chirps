from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ScanForm
from .models import Scan
from .tasks import scan_task


@login_required
def create(request):

    if request.method == 'POST':
        scan_form = ScanForm(request.POST)
        if scan_form.is_valid():

            # Save the form to the database
            scan = scan_form.save()
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
    return render(request, 'scan/dashboard.html', {'scans': Scan.objects.all()})
