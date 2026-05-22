from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(max_length=20, required=False, 
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    adresse = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'telephone', 'adresse']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = user.profile
            profile.role = 'client'  # Toujours client pour l'inscription
            profile.telephone = self.cleaned_data.get('telephone', '')
            profile.adresse = self.cleaned_data.get('adresse', '')
            profile.save()
        return user

class ForgotPasswordForm(forms.Form):
    """Formulaire pour demander une réinitialisation du mot de passe"""
    email_or_username = forms.CharField(
        label="Email ou nom d'utilisateur",
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre email ou nom d\'utilisateur',
            'autofocus': True
        })
    )

class ResetPasswordForm(forms.Form):
    """Formulaire pour réinitialiser le mot de passe"""
    password = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez votre nouveau mot de passe'
        })
    )
    password_confirm = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmez votre nouveau mot de passe'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        
        if password and len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        return cleaned_data