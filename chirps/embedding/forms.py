"""Forms for the embedding application models."""
from django import forms

from .models import Embedding


class CreateEmbeddingForm(forms.Form):
    """Form for creating embeddings."""

    text = forms.CharField(
        label='Text',
        max_length=1000,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'The text to embed'}),
    )
    model = forms.CharField(
        label='Model',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'The model to embed the text with'}),
    )
    service = forms.ChoiceField(label='Service', required=True, choices=Embedding.Service.choices)
