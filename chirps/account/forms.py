"""Form classes for the account app."""
from django import forms
from django.forms import ModelForm

from .models import Profile


class ProfileForm(ModelForm):
    """Form for the Profile model."""

    class Meta:
        """Meta class for ProfileForm."""

        model = Profile
        fields = ['openai_key']

        widgets = {'openai_key': forms.TextInput(attrs={'class': 'form-control'})}


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
