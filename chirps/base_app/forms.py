from django import forms

class InstallForm(forms.Form):

    superuser_username = forms.CharField(label='Superuser Username', max_length=100)
    superuser_email = forms.EmailField(label='Superuser Email', max_length=100)
    superuser_password = forms.CharField(label='Superuser Password', max_length=100, widget=forms.PasswordInput)
    superuser_password_confirm = forms.CharField(label='Superuser Password (Confirm)', max_length=100, widget=forms.PasswordInput)
    
