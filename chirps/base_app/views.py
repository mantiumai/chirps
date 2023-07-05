from account.models import Profile
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import InstallForm


@login_required
def index(request):
    return render(request, 'dashboard/index.html', {})

def install(request):

    # If there are uses already, redirect to the dashboard
    if User.objects.count() > 0:
        return redirect(reverse('index'))

    if request.method == 'POST':
        form = InstallForm(request.POST)
        if form.is_valid():
            # Create the user
            has_error = False
            if User.objects.filter(username=form.cleaned_data['superuser_username']).exists():
                form.add_error('superuser_username', 'Username already exists.')
                has_error = True
            if User.objects.filter(email=form.cleaned_data['superuser_email']).exists():
                form.add_error('superuser_email', 'Email already exists.')
                has_error = True
            if form.cleaned_data['superuser_password'] != form.cleaned_data['superuser_password_confirm']:
                form.add_error('superuser_password', 'Passwords do not match.')
                has_error = True

            # No errors, continue with account creation
            if has_error is False:
                # Create the user:
                user = User.objects.create_superuser(
                    form.cleaned_data['superuser_username'],
                    form.cleaned_data['superuser_email'],
                    form.cleaned_data['superuser_password']
                )

                # Create the user profile
                profile = Profile(user=user)
                profile.save()

                # Login the user
                login(request, user)

                # Redirect to the index page
                return redirect(reverse('index'))
    else:
        form = InstallForm()

    return render(request, 'dashboard/install.html', {'form': form})
