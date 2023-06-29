from django.contrib.auth import views as auth_views
from django.urls import path

from .views import profile as profile_view
from .views import signup, login_view

urlpatterns = [
    # path('login/', auth_views.LoginView.as_view(template_name='account/login.html', next_page='/'), name='login'),
    path('login/', login_view, name='login'),
    path(
        'logout/', auth_views.LogoutView.as_view(template_name='account/logout.html', next_page='login'), name='logout'
    ),
    path('signup/', signup, name='signup'),
    path('profile/', profile_view, name='profile'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'),
        name='password_reset',
    )
]
