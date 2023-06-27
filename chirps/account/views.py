from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Profile

from .forms import ProfileForm, SignupForm


def profile(request):

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)

        if form.is_valid():

            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            # Redirect the user back to the dashboard
            return redirect('profile')

    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'account/profile.html', {'form': form})

def signup(request):
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
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password1']
                )
                user.save()

                # Create the user profile
                profile = Profile(user=user)
                profile.save()

                # Login the user
                login(request, user)

                # redirect to accounts page:
                return redirect('/')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {'form': form})
