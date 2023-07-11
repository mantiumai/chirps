"""Views for the embedding app."""
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404

from .forms import CreateEmbeddingForm
from .models import Embedding
from .providers.base import BaseEmbeddingProvider, EmbeddingError


@login_required
def create(request):
    """Create a new embedding."""
    # Verify the reqquest has the requred URL parameters
    form = CreateEmbeddingForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest(json.dumps(form.errors), status=400)

    # Search for the text to see if an embedding already exists
    try:
        embedding = Embedding.objects.get(
            text=form.cleaned_data['text'],
            model=form.cleaned_data['model'],
            service=form.cleaned_data['service'],
            user=request.user,
        )
    except Embedding.DoesNotExist:  # Oh noes! We need to generate a new embedding.
        # Fetch the required provider class from the name of the service requested by the user. The service name
        # should be one of the enum values found in Embedding.Service.
        service: BaseEmbeddingProvider = Embedding.Service.get_provider_from_service_name(form.cleaned_data['service'])

        # Use the specified service to generate embeddings with the specified model
        try:
            embed_result = service.embed(
                user=request.user, model=form.cleaned_data['model'], text=form.cleaned_data['text']
            )
        except EmbeddingError as err:
            return HttpResponseBadRequest(json.dumps({'error': str(err)}), status=400)

        # Save the embedding result to the database
        embedding = Embedding.objects.create(
            model=form.cleaned_data['model'],
            service=form.cleaned_data['service'],
            text=form.cleaned_data['text'],
            vectors=embed_result,
            user=request.user,
        )

    # Return the vectors and it's siesta time.
    return JsonResponse({'embedding': embedding.vectors})


@login_required
def delete(request, embedding_id):
    """Delete an existing embedding."""
    get_object_or_404(Embedding, pk=embedding_id, user=request.user).delete()
    return HttpResponse('OK', status=200)


@login_required
def show(request):
    """List all embeddings."""
    # Paginate the number of items returned to the user, defaulting to 25 per page
    user_embeddings = Embedding.objects.filter(user=request.user).order_by('id')
    paginator = Paginator(user_embeddings, request.GET.get('item_count', 25))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return JsonResponse({'embeddings': [embedding.to_dict() for embedding in page_obj.object_list]})
