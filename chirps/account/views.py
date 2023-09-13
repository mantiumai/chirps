"""Views for the account application."""
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User  # noqa: E5142
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomPasswordChangeForm, KeyEditForm, LoginForm, ProfileForm, SignupForm
from .models import Profile


@login_required
def profile(request):
    """Render the user profile page and handle updates"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)

        if form.is_valid():
            form.save()
            messages.info(request, 'Account profile saved successfully.')

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


@login_required
def api_key_edit(request, key_name):
    """Render the API key edit page."""
    if request.method == 'POST':
        form = KeyEditForm(request.POST)
        if form.is_valid():

            if key_name == 'cohere':
                request.user.profile.cohere_key = form.cleaned_data['key']
                request.user.profile.save()
                field = request.user.profile.cohere_key
                masked_value = request.user.profile.masked_cohere_key
            elif key_name == 'openai':
                request.user.profile.openai_api_key = form.cleaned_data['key']
                request.user.profile.save()
                field = request.user.profile.openai_api_key
                masked_value = request.user.profile.masked_openai_api_key
            elif key_name == 'Anthropic':
                request.user.profile.anthropic_api_key = form.cleaned_data['key']
                request.user.profile.save()
                field = request.user.profile.anthropic_api_key
                masked_value = request.user.profile.masked_anthropic_api_key
            else:
                raise ValueError('Invalid key specified.')

            return render(
                request,
                'account/api_key_masked.html',
                {'field': field, 'key_name': key_name, 'masked_value': masked_value},
            )
    else:
        form = KeyEditForm()
    return render(request, 'account/api_key_edit.html', {'form': form, 'key_name': key_name})


@login_required
def api_key_unmasked(request, key_name):
    """Render the controls to view a masked version of the API key."""
    if key_name == 'cohere':
        value = request.user.profile.cohere_key
    elif key_name == 'openai':
        value = request.user.profile.openai_api_key
    else:
        raise ValueError('Invalid key specified.')

    return render(request, 'account/api_key_unmasked.html', {'value': value, 'key_name': key_name})


@login_required
def api_key_masked(request, key_name):
    """Fetch the masked key widget for the specified API key."""
    if key_name == 'cohere':
        masked_value = request.user.profile.masked_cohere_key
    elif key_name == 'openai':
        masked_value = request.user.profile.masked_openai_api_key
    elif key_name == 'Anthropic':
        masked_value = request.user.profile.masked_anthropic_api_key
    else:
        raise ValueError('No key specified.')

    return render(request, 'account/api_key_masked.html', {'key_name': key_name, 'masked_value': masked_value})


class CustomPasswordChangeView(PasswordChangeView):
    """Custom auth view"""

    form_class = CustomPasswordChangeForm

    def form_valid(self, form):
        """Override the form_valid method to add a success message"""
        response = super().form_valid(form)
        messages.success(self.request, 'Your password was successfully updated!')
        return response
