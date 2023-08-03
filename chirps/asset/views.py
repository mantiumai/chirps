"""View handlers for assets."""
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from embedding.models import Embedding

from .forms import asset_from_html_name, assets, form_from_model
from .models import BaseAsset, PingResult


@login_required
def dashboard(request):
    """Render the dashboard for the asset app.

    Args:
        request (HttpRequest): Django request object
    """
    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_assets = BaseAsset.objects.filter(user=request.user).order_by('id')
    paginator = Paginator(user_assets, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'asset/dashboard.html', {'available_assets': assets, 'page_obj': page_obj})


@login_required
def create(request, html_name):
    """Render the create asset form.

    Args:
        request (HttpRequest): Django request object
        html_name (str): used to get the asset dictionary entry
    """
    if request.method == 'POST':

        # Get the asset dictionary entry from the html_name parameter
        asset = asset_from_html_name(html_name=html_name)
        form = asset['form'](request.POST)

        if form.is_valid():

            # Persist the
            form.user = request.user

            # Convert the form into an asset object (don't persist to the DB yet)
            asset = form.save(commit=False)

            # Assign the asset to the current user
            asset.user = request.user

            # Off to the DB we go!
            asset.save()

            # Redirect the user back to the dashboard
            return redirect('asset_dashboard')

    else:
        asset = asset_from_html_name(html_name=html_name)
        form = asset['form']()

    default_service = Embedding.Service.OPEN_AI
    service_model_choices = Embedding.get_models_for_service(default_service)
    context = {
        'form': form,
        'asset': asset,
        'service_model_choices': service_model_choices,
    }
    return render(request, 'asset/create.html', context)


@login_required
def get_embedding_models(request):
    """Get available embedding models based on selected service"""
    service = request.GET.get('service', None)
    models = Embedding.get_models_for_service(service)
    return JsonResponse(models, safe=False)


@login_required
def edit(request, asset_id):
    """Display the asset with its creation fields - but populated and ready to edit."""
    asset = get_object_or_404(BaseAsset, pk=asset_id, user=request.user)

    if request.method == 'POST':
        form = form_from_model(asset)(request.POST, instance=asset)
        if form.is_valid():

            # Quick double check to make sure the asset isn't being used by a scan
            if asset.scan_is_active():
                messages.error(request, 'Unable to edit asset while a scan is active.')
            else:
                form.save()
                messages.info(request, 'Asset changes saved.')
                return redirect('asset_dashboard')
    else:
        form = form_from_model(asset)(instance=asset)

    return render(request, 'asset/edit.html', {'form': form, 'asset': asset})


@login_required
def ping(request, asset_id):
    """Ping a RedisAsset database using the test_connection() function."""
    asset = get_object_or_404(BaseAsset, pk=asset_id)

    # Double check to make sure the asset supports the ping operation
    if asset.HAS_PING is False:
        return HttpResponseBadRequest(
            json.dumps({'success': False, 'error': 'Asset does not support a ping operation'}),
            content_type='application/json',
        )

    # Attempt to ping the asset
    result: PingResult = asset.test_connection()

    # If the ping was unsuccessful, return the error message
    if result.success is False:
        return HttpResponseBadRequest(
            json.dumps({'success': False, 'error': result.error}), content_type='application/json'
        )

    # All is well, it's party time!
    return JsonResponse({'success': True})


@login_required
def delete(request, asset_id):   # pylint: disable=unused-argument
    """Delete an asset from the database."""
    get_object_or_404(BaseAsset, pk=asset_id).delete()
    return redirect('asset_dashboard')
