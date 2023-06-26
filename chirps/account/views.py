from django.shortcuts import redirect, render

from .forms import ProfileForm


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
