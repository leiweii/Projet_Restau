from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("password_confirm")
        if password and confirm and password != confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    telephone = forms.CharField(max_length=20, required=False)
    preferences = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email']
    
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)
        if profile:
            self.fields['telephone'].initial = profile.telephone
            self.fields['preferences'].initial = profile.preferences

    def save(self, user_instance, profile_instance, commit=True):
        user_instance.username = self.cleaned_data['username']
        user_instance.email = self.cleaned_data['email']
        if commit:
            user_instance.save()

        profile_instance.telephone = self.cleaned_data['telephone']
        profile_instance.preferences = self.cleaned_data['preferences']
        if commit:
            profile_instance.save()
