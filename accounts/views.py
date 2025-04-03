from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileUpdateForm
from django.contrib import messages



def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_update_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user, profile=profile)
        if form.is_valid():
            form.save(user_instance=user, profile_instance=profile)
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profile')
    else:
        form = UserProfileUpdateForm(instance=user, profile=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})