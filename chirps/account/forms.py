"""Form classes for the account app."""
from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    """User profile form"""

    finding_preview_size = forms.IntegerField(
        initial=20,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20'}),
    )

    class Meta:
        model = Profile
        fields = ['finding_preview_size']


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


class KeyEditForm(forms.Form):
    """Form for editing keys."""

    key = forms.CharField(max_length=256)
