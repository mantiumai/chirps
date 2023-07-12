"""Views for the embedding app."""
import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404

from .forms import CreateEmbeddingForm
from .models import Embedding
from .providers.base import EmbeddingError
from .utils import create_embedding


@login_required
def create(request):
    """Create a new embedding."""
    # Verify the reqquest has the requred URL parameters
    form = CreateEmbeddingForm(request.GET)
    if not form.is_valid():
        return HttpResponseBadRequest(json.dumps(form.errors), status=400)

    # Use the specified service to generate embeddings with the specified model
    try:
        embedding: Embedding = create_embedding(
            text=form.cleaned_data['text'],
            model=form.cleaned_data['model'],
            service=form.cleaned_data['service'],
            user=request.user,
        )
    except EmbeddingError as err:
        return HttpResponseBadRequest(json.dumps({'error': str(err)}), status=400)

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
