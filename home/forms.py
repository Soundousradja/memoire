from django import forms
from SuperAdmin.models import Restaurant
from SuperAdmin.models import Admin
from django.contrib.auth.forms import AuthenticationForm

from django.forms import modelformset_factory

from django.contrib.auth.forms import UserCreationForm 
from .models import CustomUser


class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d’utilisateur', max_length=100)
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label="Adresse e-mail")

class PasswordResetForm(DjangoSetPasswordForm):
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )
    # In app/forms.py
class ClientRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=True)

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password']
        )
        user.role = 'client'
        if commit:
            user.save()
        return user
