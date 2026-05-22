from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncDay
from users.forms import UserRegisterForm
from django.utils import timezone
from datetime import timedelta
from stock.models import Medicament
from ventes.models import Vente, DetailVente

@login_required
def dashboard_admin(request):
    """Dashboard pour administrateur avec statistiques"""
    
    # Vérifier que l'utilisateur est admin ou pharmacien
    if request.user.profile.role not in ['admin', 'pharmacien']:
        return render(request, 'dashboard/access_denied.html')
    
    # === Statistiques générales ===
    total_medicaments = Medicament.objects.count()
    medicaments_rupture = Medicament.objects.filter(quantite_stock=0).count()
    medicaments_critique = Medicament.objects.filter(quantite_stock__lte=models.F('seuil_alerte')).count()
    medicaments_expires = Medicament.objects.filter(date_expiration__lt=timezone.now().date()).count()
    
    # === Chiffre d'affaires ===
    ca_total = Vente.objects.filter(statut='terminee').aggregate(total=Sum('total_ttc'))['total'] or 0
    aujourdhui = timezone.now().date()
    ca_aujourdhui = Vente.objects.filter(statut='terminee', date_vente__date=aujourdhui).aggregate(total=Sum('total_ttc'))['total'] or 0
    
    debut_semaine = aujourdhui - timedelta(days=aujourdhui.weekday())
    ca_semaine = Vente.objects.filter(statut='terminee', date_vente__date__gte=debut_semaine).aggregate(total=Sum('total_ttc'))['total'] or 0
    
    debut_mois = aujourdhui.replace(day=1)
    ca_mois = Vente.objects.filter(statut='terminee', date_vente__date__gte=debut_mois).aggregate(total=Sum('total_ttc'))['total'] or 0
    
    # === Ventes ===
    total_ventes = Vente.objects.filter(statut='terminee').count()
    ventes_aujourdhui = Vente.objects.filter(statut='terminee', date_vente__date=aujourdhui).count()
    
    # === Top médicaments vendus ===
    top_medicaments = DetailVente.objects.values('medicament__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')[:5]
    
    # === Graphique ventes 7 derniers jours ===
    ventes_par_jour = []
    for i in range(6, -1, -1):
        jour = aujourdhui - timedelta(days=i)
        total = Vente.objects.filter(statut='terminee', date_vente__date=jour).aggregate(total=Sum('total_ttc'))['total'] or 0
        ventes_par_jour.append({'jour': jour.strftime('%d/%m'), 'total': float(total)})
    
    # === Statistiques supplémentaires ===
    total_utilisateurs = User.objects.count()
    croissance_ventes = 12.5
    
    # Calculer les ventes par catégorie (si vous avez un champ catégorie)
    # Sinon, on groupe par médicament
    try:
        ventes_categorie = DetailVente.objects.values('medicament__nom').annotate(
            total_ventes=Sum('sous_total')
        ).order_by('-total_ventes')[:5]
    except:
        ventes_categorie = []
    
    # Activités récentes (à remplacer par de vraies données plus tard)
    activites_recentes = [
        {'date': timezone.now(), 'action': 'Nouvelle vente', 'user': request.user.username, 'details': 'Commande validée'},
        {'date': timezone.now() - timedelta(hours=2), 'action': 'Alerte stock', 'user': 'Système', 'details': 'Stock critique détecté'},
        {'date': timezone.now() - timedelta(days=1), 'action': 'Ajout médicament', 'user': 'Pharmacien', 'details': 'Nouveau produit ajouté'},
    ]
    
    context = {
        'total_medicaments': total_medicaments,
        'medicaments_rupture': medicaments_rupture,
        'medicaments_critique': medicaments_critique,
        'medicaments_expires': medicaments_expires,
        'ca_total': ca_total,
        'ca_aujourdhui': ca_aujourdhui,
        'ca_semaine': ca_semaine,
        'ca_mois': ca_mois,
        'total_ventes': total_ventes,
        'ventes_aujourdhui': ventes_aujourdhui,
        'top_medicaments': top_medicaments,
        'ventes_par_jour': ventes_par_jour,
        'total_utilisateurs': total_utilisateurs,
        'ventes_categorie': ventes_categorie,
        'activites_recentes': activites_recentes,
        'croissance_ventes': croissance_ventes,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def manage_users(request):
    if request.user.profile.role != 'admin':
        return render(request, 'dashboard/access_denied.html')

    connected_users = User.objects.filter(is_active=True, last_login__isnull=False).order_by('-last_login')
    all_users = User.objects.all().order_by('username')

    if request.method == 'POST':
        if 'toggle_status' in request.POST:
            user_id = request.POST.get('user_id')
            action = request.POST.get('action')
            try:
                target_user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                messages.error(request, 'Utilisateur introuvable.')
                return redirect('dashboard:manage_users')

            if target_user == request.user and action == 'block':
                messages.error(request, 'Vous ne pouvez pas bloquer votre propre compte.')
            else:
                if action == 'block':
                    target_user.is_active = False
                    target_user.save()
                    messages.success(request, f'Utilisateur {target_user.username} bloqué.')
                elif action == 'unblock':
                    target_user.is_active = True
                    target_user.save()
                    messages.success(request, f'Utilisateur {target_user.username} débloqué.')

            return redirect('dashboard:manage_users')

        if 'add_user' in request.POST:
            form = UserRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Nouvel utilisateur créé avec succès.')
                return redirect('dashboard:manage_users')
            else:
                messages.error(request, 'Veuillez corriger les erreurs du formulaire.')
    else:
        form = UserRegisterForm()

    context = {
        'connected_users': connected_users,
        'all_users': all_users,
        'form': form,
    }
    return render(request, 'dashboard/manage_users.html', context)
@login_required
def edit_user(request, user_id):
    if request.user.profile.role != 'admin':
        return render(request, 'dashboard/access_denied.html')
    
    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('dashboard:manage_users')
    
    if request.method == 'POST':
        target_user.username = request.POST.get('username', target_user.username)
        target_user.email = request.POST.get('email', target_user.email)
        target_user.save()
        
        target_user.profile.role = request.POST.get('role', target_user.profile.role)
        target_user.profile.telephone = request.POST.get('telephone', target_user.profile.telephone)
        target_user.profile.save()
        
        messages.success(request, f'Utilisateur {target_user.username} modifié avec succès.')
        return redirect('dashboard:manage_users')
    
    return render(request, 'dashboard/edit_user.html', {'target_user': target_user})


@login_required
def delete_user(request, user_id):
    if request.user.profile.role != 'admin':
        return render(request, 'dashboard/access_denied.html')
    
    try:
        target_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('dashboard:manage_users')
    
    if target_user == request.user:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('dashboard:manage_users')
    
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'Utilisateur {username} supprimé avec succès.')
        return redirect('dashboard:manage_users')
    
    return render(request, 'dashboard/delete_user.html', {'target_user': target_user})