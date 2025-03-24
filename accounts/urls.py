from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, profile_view, profile_update_view

urlpatterns = [
    path('inscription/', register_view, name='register'),
    path('connexion/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', profile_view, name='profile'),
    path('profil/modifier/', profile_update_view, name='profile_edit'),
]
