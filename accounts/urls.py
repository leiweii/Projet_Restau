from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, profile_view, profile_update_view

urlpatterns = [
    path('inscription/', register_view, name='register'),
    path('connexion/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', profile_view, name='profile'),
    path('profil/modifier/', profile_update_view, name='profile_edit'),

    path('profil/password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/password_change.html',
        success_url='/compte/profil/'
    ), name='password_change'),

    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('mot-de-passe-envoye/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reinitialiser/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('mot-de-passe-modifie/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),

]
