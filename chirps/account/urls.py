"""URLs for the account app."""
from django.contrib.auth import views as auth_views
from django.urls import path

from .views import api_key_edit, api_key_masked, api_key_unmasked, login_view
from .views import profile as profile_view
from .views import signup

urlpatterns = [
    path('login/', login_view, name='login'),
    path(
        'logout/', auth_views.LogoutView.as_view(template_name='account/logout.html', next_page='login'), name='logout'
    ),
    path('api_key_masked/<str:key_name>', api_key_masked, name='api_key_masked'),
    path('api_key_unmasked/<str:key_name>', api_key_unmasked, name='api_key_unmasked'),
    path('api_key_edit/<str:key_name>', api_key_edit, name='api_key_edit'),
    path('profile/', profile_view, name='profile'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'),
        name='password_reset',
    ),
    path('signup/', signup, name='signup'),
]
