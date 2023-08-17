"""Form classes for the account app."""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm

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


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom form for changing password"""

    def __init__(self, *args, **kwargs):
        """Style input fields with Bootstrap"""
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
