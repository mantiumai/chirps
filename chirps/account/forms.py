from django import forms
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm

from .models import Profile


class ProfileForm(ModelForm):
    def clean_openai_key(self):
        data = self.cleaned_data['openai_key']
        return make_password(data)

    class Meta:
        model = Profile
        fields = ['openai_key']

        widgets = {'openai_key': forms.PasswordInput(attrs={'class': 'form-control'})}
