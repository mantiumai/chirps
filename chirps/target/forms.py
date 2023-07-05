from django import forms
from django.forms import ModelForm

from .models import MantiumTarget, RedisTarget


class RedisTargetForm(ModelForm):
    class Meta:
        model = RedisTarget
        fields = ['name', 'host', 'port', 'database_name', 'username', 'password']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}),
            'host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hostname or IP address'}),
            'port': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '6379'}),
            'database_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Database name'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'guest'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class MantiumTargetForm(ModelForm):
    class Meta:
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
    class Meta:  
        model = PineconeTarget  
        fields = [  
            'name',  
            'api_key',  
            'environment',  
            'index_name',  
            'project_name',  
        ]  
  
        widgets = {  
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a name for the target'}),  
            'api_key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'API Key'}),  
            'environment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Environment (optional)'}),  
            'index_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Index Name (optional)'}),  
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name (optional)'}),  
        }  


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

