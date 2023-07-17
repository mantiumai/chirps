"""Forms for rendering and validating the target models."""
from django import forms
from django.forms import ModelForm

from .providers.mantium import MantiumTarget
from .providers.pinecone import PineconeTarget
from .providers.redis import RedisTarget


class RedisTargetForm(ModelForm):
    """Form for the RedisTarget model."""

    class Meta:
        """Django Meta options for the RedisTargetForm."""

        model = RedisTarget
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
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}),
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


class MantiumTargetForm(ModelForm):
    """Form for the MantiumTarget model."""

    class Meta:
        """Django Meta options for the MantiumTargetForm."""

        model = MantiumTarget
        fields = [
            'name',
            'app_id',
            'client_id',
            'client_secret',
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}),
            'app_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Application ID'}),
            'client_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client ID'}),
            'client_secret': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class PineconeTargetForm(ModelForm):    
    """Form for the PineconeTarget model."""    
    
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
        """Django Meta options for the PineconeTargetForm."""    
    
        model = PineconeTarget    
        fields = [    
            'name',    
            'api_key',    
            'environment',    
            'index_name',    
            'project_name',    
            'metadata_text_field',    
        ]    

    def __init__(self, *args, **kwargs):
        super(PineconeTargetForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'})
        self.fields['api_key'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'})
        self.fields['environment'].widget = forms.Select(choices=self.ENV_CHOICES, attrs={'class': 'form-control'})
        self.fields['index_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Index Name', 'required': True})
        self.fields['project_name'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name (optional)'})
        self.fields['metadata_text_field'].widget = forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Metadata field in which text is stored'})

targets = [
    {'form': RedisTargetForm, 'model': RedisTarget},
    {'form': MantiumTargetForm, 'model': MantiumTarget},
    {'form': PineconeTargetForm, 'model': PineconeTarget},
]


def target_from_html_name(html_name: str) -> dict:
    """Return the form class for the specified html_name."""
    for target in targets:
        if target['model'].html_name == html_name:
            return target

    return {}
