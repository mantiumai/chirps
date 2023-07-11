"""Views for the account application."""
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User  # noqa: E5142
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm, ProfileForm, SignupForm
from .models import Profile


def profile(request):
    """Render the user profile page and handle updates"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)

        if form.is_valid():

            profile_form = form.save(commit=False)
            profile_form.user = request.user
            profile_form.save()

            # Redirect the user back to the dashboard
            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'account/profile.html', {'form': form})


def signup(request):
    """Render the signup page and handle posts."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create the user
            has_error = False
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username already exists.')
                has_error = True
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                form.add_error('email', 'Email already exists.')
                has_error = True
            if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                form.add_error('password1', 'Passwords do not match.')
                has_error = True

            # No errors, continue with account creation
            if has_error is False:
                # Create the user:
                user = User.objects.create_user(
                    form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1']
                )
                user.save()

                # Create the user profile
                user_profile = Profile(user=user)
                user_profile.save()

                # Login the user
                login(request, user)

                # redirect to accounts page:
                return redirect('/')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {'form': form})


def login_view(request):
    """Render the login page."""
    # If there are no users, redirect to the installation page
    if User.objects.count() == 0:
        return redirect(reverse('install'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request=request, username=form.cleaned_data['username'], password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('/')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})
