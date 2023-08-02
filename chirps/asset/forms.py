"""Forms for rendering and validating the asset models."""
from django import forms
from django.forms import ModelForm
from embedding.models import Embedding

from .providers.mantium import MantiumAsset
from .providers.pinecone import PineconeAsset
from .providers.redis import RedisAsset


class RedisAssetForm(ModelForm):
    """Form for the RedisAsset model."""

    embedding_model_service = forms.ChoiceField(
        choices=Embedding.Service.choices,
        widget=forms.SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': 'true', 'data-size': '10'}),
        required=True,
    )

    class Meta:
        """Django Meta options for the RedisAssetForm."""

        model = RedisAsset
        fields = [
            'name',
            'host',
            'port',
            'database_name',
            'username',
            'password',
            'index_name',
            'text_field',
            'embedding_field',
            'embedding_model',
            'embedding_model_service',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the asset'}),
            'host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hostname or IP address'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '6379'}),
            'database_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Database name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'guest'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'index_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'The name of the index in which documents are stored'}
            ),
            'text_field': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'The document field in which text is stored'}
            ),
            'embedding_field': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'The document field in which embeddings are stored'}
            ),
            'embedding_model': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'The model that generated the embeddings'}
            ),
        }


class MantiumAssetForm(ModelForm):
    """Form for the MantiumAsset model."""

    class Meta:
        """Django Meta options for the MantiumAssetForm."""

        model = MantiumAsset
        fields = [
            'name',
            'app_id',
            'client_id',
            'client_secret',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the asset'}),
            'app_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Application ID'}),
            'client_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client ID'}),
            'client_secret': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class PineconeAssetForm(ModelForm):
    """Form for the PineconeAsset model."""

    ENV_CHOICES = [
        ('us-west4-gcp-free', 'us-west4-gcp-free'),
        ('us-west1-gcp-free', 'us-west1-gcp-free'),
        ('asia-southeast1-gcp-free', 'asia-southeast1-gcp-free'),
        ('eu-west4-gcp', 'eu-west4-gcp'),
        ('northamerica-northeast1-gcp', 'northamerica-northeast1-gcp'),
        ('asia-northeast1-gcp', 'asia-northeast1-gcp'),
        ('asia-southeast1-gcp', 'asia-southeast1-gcp'),
        ('us-east4-gcp', 'us-east4-gcp'),
        ('us-west4-gcp', 'us-west4-gcp'),
        ('us-central1-gcp', 'us-central1-gcp'),
        ('us-west1-gcp', 'us-west1-gcp'),
        ('us-east1-gcp', 'us-east1-gcp'),
        ('eu-west1-gcp', 'eu-west1-gcp'),
        ('us-east-1-aws', 'us-east-1-aws'),
    ]

    embedding_model_service = forms.ChoiceField(
        choices=Embedding.Service.choices,
        widget=forms.SelectMultiple(attrs={'class': 'selectpicker', 'data-live-search': 'true', 'data-size': '10'}),
        required=True,
    )

    class Meta:
        """Django Meta options for the PineconeAssetForm."""

        model = PineconeAsset
        fields = [
            'name',
            'api_key',
            'environment',
            'index_name',
            'project_name',
            'metadata_text_field',
            'embedding_model',
            'embedding_model_service',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter a name for the asset'}
        )
        self.fields['api_key'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'})
        self.fields['environment'].widget = forms.Select(choices=self.ENV_CHOICES, attrs={'class': 'form-control'})
        self.fields['index_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Index Name', 'required': True}
        )
        self.fields['project_name'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Project Name (optional)'}
        )
        self.fields['metadata_text_field'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Metadata field in which text is stored'}
        )
        self.fields['embedding_model'].widget = forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'The model that generated the embeddings'}
        )


assets = [
    {'form': RedisAssetForm, 'model': RedisAsset},
    {'form': MantiumAssetForm, 'model': MantiumAsset},
    {'form': PineconeAssetForm, 'model': PineconeAsset},
]


def asset_from_html_name(html_name: str) -> dict:
    """Return the form class for the specified html_name."""
    for asset in assets:
        if asset['model'].html_name == html_name:
            return asset

    return {}
