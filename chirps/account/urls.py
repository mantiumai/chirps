"""URLs for the account app."""
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import get_cohere_key, get_openai_key, login_view
from .views import profile as profile_view
from .views import signup

urlpatterns = [
    path('login/', login_view, name='login'),
    path(
        'logout/', auth_views.LogoutView.as_view(template_name='account/logout.html', next_page='login'), name='logout'
    ),
    path('openai_key', get_openai_key, name='get_openai_key'),
    path('cohere_key', get_cohere_key, name='get_cohere_key'),
    path('profile/', profile_view, name='profile'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'),
        name='password_reset',
    ),
    path('signup/', signup, name='signup'),
]
