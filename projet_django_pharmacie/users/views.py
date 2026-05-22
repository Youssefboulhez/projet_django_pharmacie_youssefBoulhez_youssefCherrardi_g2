from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_http_methods
from .forms import UserRegisterForm, ForgotPasswordForm, ResetPasswordForm

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)
        if user is None:
            # Essayer par email si la connexion par identifiant échoue
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Bienvenue {user.username} !')
            
            # Redirection basée sur le rôle
            if user.profile.role == 'admin':
                return redirect('dashboard:index')
            elif user.profile.role == 'pharmacien':
                return redirect('stock:liste_medicaments')  # ou une page dashboard pharmacien
            else:  # client
                return redirect('stock:liste_medicaments')
        else:
            messages.error(request, '❌ Email/nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'users/login.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'✅ Bienvenue {user.username} !')
            return redirect('stock:liste_medicaments')
        else:
            messages.error(request, f'❌ Erreurs : {form.errors}')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    """Affiche et modifie le profil utilisateur"""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.save()
        
        profile = user.profile
        profile.telephone = request.POST.get('telephone', '')
        profile.adresse = request.POST.get('adresse', '')
        profile.save()
        
        messages.success(request, '✅ Votre profil a été mis à jour !')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html', {'user': request.user})

@require_http_methods(["GET", "POST"])
def forgot_password_request(request):
    """Page pour demander la réinitialisation du mot de passe"""
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email_or_username = form.cleaned_data['email_or_username']
            
            # Chercher l'utilisateur par email ou username
            try:
                user = User.objects.get(email__iexact=email_or_username) or \
                       User.objects.get(username__iexact=email_or_username)
            except User.DoesNotExist:
                # Pour des raisons de sécurité, ne pas révéler si l'utilisateur existe
                messages.info(request, '✅ Si cet utilisateur existe, un email de réinitialisation a été envoyé.')
                return redirect('users:forgot_password_request')
            
            # Générer le token de réinitialisation
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Construire le lien de réinitialisation
            reset_url = request.build_absolute_uri(
                reverse('users:forgot_password_reset', kwargs={'uid': uid, 'token': token})
            )
            
            # Préparer le message email
            subject = 'Réinitialisation de votre mot de passe - Pharmacie PharmaGest'
            message = f"""
Bonjour {user.first_name or user.username},

Vous avez demandé une réinitialisation de mot de passe. Cliquez sur le lien ci-dessous pour réinitialiser votre mot de passe :

{reset_url}

Ce lien expirera dans 1 heure.

Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.

Cordialement,
L'équipe Pharmacie PharmaGest
            """
            
            html_message = f"""
<h2>Réinitialisation de mot de passe</h2>
<p>Bonjour {user.first_name or user.username},</p>
<p>Vous avez demandé une réinitialisation de mot de passe. Cliquez sur le lien ci-dessous :</p>
<p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Réinitialiser mon mot de passe</a></p>
<p>Ce lien expirera dans 1 heure.</p>
<p>Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.</p>
<p>Cordialement,<br>L'équipe Pharmacie PharmaGest</p>
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@pharmacie.local',
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, '✅ Un email de réinitialisation a été envoyé à votre adresse email.')
            except Exception as e:
                messages.warning(request, f'⚠️ Email envoyé localement (serveur email non configuré). Token: {token}')
            
            return redirect('users:login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'users/forgot_password_request.html', {'form': form})

@require_http_methods(["GET", "POST"])
def forgot_password_reset(request, uid, token):
    """Page pour réinitialiser le mot de passe avec token"""
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, '❌ Lien de réinitialisation invalide ou expiré.')
        return redirect('users:forgot_password_request')
    
    # Vérifier la validité du token
    if not default_token_generator.check_token(user, token):
        messages.error(request, '❌ Lien de réinitialisation expiré.')
        return redirect('users:forgot_password_request')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            
            messages.success(request, '✅ Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'users/forgot_password_reset.html', {
        'form': form,
        'uid': uid,
        'token': token,
        'username': user.username
    })