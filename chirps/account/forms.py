"""Form classes for the account app."""
from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    """User profile form"""

    openai_key = forms.CharField(
        max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cohere_key = forms.CharField(
        max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['openai_key', 'cohere_key']


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
