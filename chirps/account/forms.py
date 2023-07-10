"""Form classes for the account app."""
from django import forms
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm

from .models import Profile


class ProfileForm(ModelForm):
    """Form for the Profile model."""

    def clean_openai_key(self):
        """Hash the openai_key before saving it to the database."""
        data = self.cleaned_data['openai_key']
        return make_password(data)

    class Meta:
        """Meta class for ProfileForm."""

        model = Profile
        fields = ['openai_key']

        widgets = {'openai_key': forms.PasswordInput(attrs={'class': 'form-control'})}


class LoginForm(forms.Form):
    """Form for logging in."""

    username = forms.CharField(max_length=256)
    password = forms.CharField(max_length=256, widget=forms.PasswordInput)


class SignupForm(forms.Form):
    """Form for signing up."""

    username = forms.CharField(max_length=256)
    email = forms.EmailField(max_length=256)
    password1 = forms.CharField(max_length=256, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=256, widget=forms.PasswordInput)
