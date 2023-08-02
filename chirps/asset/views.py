"""View handlers for assets."""
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from embedding.models import Embedding
from redis import exceptions

from .forms import asset_from_html_name, assets
from .models import BaseAsset
from .providers.pinecone import PineconeAsset
from .providers.redis import RedisAsset


def decrypted_keys(request):
    """Return a list of decrypted API keys for all Pinecone assets."""
    keys = []
    for asset in PineconeAsset.objects.all():
        keys.append(asset.decrypted_api_key)
    return JsonResponse({'keys': keys})


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


def get_embedding_models(request):
    """Get available embedding models based on selected service"""
    service = request.GET.get('service', None)
    models = Embedding.get_models_for_service(service)
    return JsonResponse(models, safe=False)


@login_required
def ping(request, asset_id):
    """Ping a RedisAsset database using the test_connection() function."""
    asset = get_object_or_404(BaseAsset, pk=asset_id)
    if isinstance(asset, RedisAsset):
        try:
            result = asset.test_connection()
            return JsonResponse({'success': result})
        except exceptions.ConnectionError:
            return HttpResponseBadRequest(
                json.dumps({'success': False, 'error': 'Unable to connect to Redis'}), content_type='application/json'
            )
    return HttpResponseBadRequest(json.dumps({'success': False, 'error': 'Not a RedisAsset'}))


@login_required
def delete(request, asset_id):   # pylint: disable=unused-argument
    """Delete an asset from the database."""
    get_object_or_404(BaseAsset, pk=asset_id).delete()
    return redirect('asset_dashboard')
