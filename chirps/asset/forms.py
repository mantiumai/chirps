"""Forms for rendering and validating the asset models."""
from asset.models import BaseAsset
from asset.widgets import KeyValueWidget
from django import forms
from django.forms import ModelForm
from django.urls import reverse_lazy
from embedding.models import Embedding

from .providers.api_endpoint import APIEndpointAsset
from .providers.mantium import MantiumAsset
from .providers.pinecone import PineconeAsset
from .providers.redis import RedisAsset


class VectorDatabaseAssetForm(ModelForm):
    """Base form class for assets with shared fields."""

    default_service = Embedding.Service.OPEN_AI

    embedding_model_service = forms.ChoiceField(
        choices=Embedding.Service.choices,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'hx-get': reverse_lazy('embedding_models'),
                'hx-target': '#id_embedding_model',
                'hx-indicator': '.htmx-indicator',
            }
        ),
        required=True,
        initial=default_service,
    )
    embedding_model = forms.ChoiceField(
        choices=Embedding.get_models_for_service(default_service),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        abstract = True
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the asset'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            service = self.data.get('embedding_model_service', self.default_service)
        else:
            service = self.initial.get('embedding_model_service', self.default_service)
        self.fields['embedding_model'].choices = Embedding.get_models_for_service(service)


class RedisAssetForm(VectorDatabaseAssetForm):
    """Form for the RedisAsset model."""

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
            'embedding_model_service',
            'embedding_model',
        ]

        widgets = {
            **VectorDatabaseAssetForm.Meta.widgets,
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


class PineconeAssetForm(VectorDatabaseAssetForm):
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
            'embedding_model_service',
            'embedding_model',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for widget_name, value in VectorDatabaseAssetForm.Meta.widgets.items():
            self.fields[widget_name].widget = value

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


class APIEndpointAssetForm(ModelForm):
    """Form for the APIEndpointAsset model."""

    class Meta:
        """Django Meta options for the APIEndpointAssetForm."""

        model = APIEndpointAsset
        fields = [
            'name',
            'description',
            'url',
            'authentication_method',
            'api_key',
            'headers',
            'body',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the asset'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'What does this API endpoint do?'}
            ),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
            'authentication_method': forms.Select(
                choices=[('Basic', 'Basic'), ('Bearer', 'Bearer')], attrs={'class': 'form-control'}
            ),
            'api_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'}),
            'headers': KeyValueWidget(attrs={'class': 'form-control'}),
            'body': KeyValueWidget(attrs={'class': 'form-control'}),
        }


assets = [
    {'form': RedisAssetForm, 'model': RedisAsset},
    {'form': MantiumAssetForm, 'model': MantiumAsset},
    {'form': PineconeAssetForm, 'model': PineconeAsset},
    {'form': APIEndpointAssetForm, 'model': APIEndpointAsset},
]


def asset_from_html_name(html_name: str) -> dict:
    """Return the form class for the specified html_name."""
    for asset in assets:
        if asset['model'].html_name == html_name:
            return asset

    return {}


def form_from_model(model: BaseAsset) -> ModelForm:
    """Return the form class for the specified model."""
    for asset in assets:
        if asset['model'] == type(model):
            return asset['form']

    return None
