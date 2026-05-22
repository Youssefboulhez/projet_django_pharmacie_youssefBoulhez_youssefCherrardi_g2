from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Medicament
from .forms import MedicamentForm
import pandas as pd
from django.http import HttpResponse
import csv
from io import StringIO, TextIOWrapper
from django.core.mail import send_mail
from django.conf import settings
from .models import Medicament, Fournisseur
from .forms import MedicamentForm, FournisseurForm

def home(request):
    """Page d'accueil avec boutons connexion/inscription et carrousel de médicaments"""
    # Récupérer les médicaments avec photos
    medicaments = Medicament.objects.filter(image__isnull=False).exclude(image='').order_by('-date_ajout')[:10]
    
    return render(request, 'home.html', {'medicaments': medicaments})

def liste_medicaments(request):
    """Affiche la liste de tous les médicaments - Accès public"""
    medicaments = Medicament.objects.all()
    
    # Filtres
    forme_filter = request.GET.get('forme', '')
    recherche = request.GET.get('q', '')
    
    if forme_filter:
        medicaments = medicaments.filter(forme__icontains=forme_filter)
    
    if recherche:
        medicaments = medicaments.filter(
            models.Q(nom__icontains=recherche) | 
            models.Q(description__icontains=recherche)
        )
    
    # Récupérer les formes disponibles pour le filtre
    formes_disponibles = Medicament.objects.values_list('forme', flat=True).distinct().exclude(forme__isnull=True).exclude(forme='')
    
    context = {
        'medicaments': medicaments,
        'titre': 'Liste des médicaments',
        'forme_filter': forme_filter,
        'recherche': recherche,
        'formes_disponibles': formes_disponibles
    }
    return render(request, 'stock/medicament_liste.html', context)

def rechercher_medicaments(request):
    """Recherche avancée des médicaments - Accès public"""
    query = request.GET.get('q', '')
    categorie = request.GET.get('categorie', '')
    prix_min = request.GET.get('prix_min', '')
    prix_max = request.GET.get('prix_max', '')
    en_stock = request.GET.get('en_stock', '')
    
    medicaments = Medicament.objects.all()
    
    # Recherche textuelle
    if query:
        medicaments = medicaments.filter(
            models.Q(nom__icontains=query) | 
            models.Q(code_barre__icontains=query) |
            models.Q(description__icontains=query)
        )
    
    # Filtre par catégorie (si vous ajoutez un champ categorie plus tard)
    # if categorie:
    #     medicaments = medicaments.filter(categorie=categorie)
    
    # Filtre par prix
    if prix_min:
        try:
            medicaments = medicaments.filter(prix_vente__gte=float(prix_min))
        except ValueError:
            pass
    
    if prix_max:
        try:
            medicaments = medicaments.filter(prix_vente__lte=float(prix_max))
        except ValueError:
            pass
    
    # Filtre stock
    if en_stock == 'oui':
        medicaments = medicaments.filter(quantite_stock__gt=0)
    elif en_stock == 'non':
        medicaments = medicaments.filter(quantite_stock=0)
    
    context = {
        'medicaments': medicaments,
        'query': query,
        'categorie': categorie,
        'prix_min': prix_min,
        'prix_max': prix_max,
        'en_stock': en_stock,
        'resultats': medicaments.count()
    }
    return render(request, 'stock/medicament_recherche.html', context)

@login_required
def ajouter_medicament(request):
    """Ajouter un nouveau médicament - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES)
        if form.is_valid():
            medicament = form.save()
            messages.success(request, f'Médicament "{medicament.nom}" ajouté avec succès !')
            return redirect('stock:liste_medicaments')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez corriger les champs.')
    else:
        form = MedicamentForm()
    
    return render(request, 'stock/medicament_form.html', {'form': form, 'titre': 'Ajouter un médicament'})

@login_required
def modifier_medicament(request, pk):
    """Modifier un médicament existant - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    medicament = get_object_or_404(Medicament, pk=pk)
    
    if request.method == 'POST':
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
        if form.is_valid():
            form.save()
            messages.success(request, f'Médicament "{medicament.nom}" modifié avec succès !')
            return redirect('stock:liste_medicaments')
    else:
        form = MedicamentForm(instance=medicament)
    
    return render(request, 'stock/medicament_form.html', {'form': form, 'titre': 'Modifier le médicament'})

@login_required
def supprimer_medicament(request, pk):
    """Supprimer un médicament - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    medicament = get_object_or_404(Medicament, pk=pk)
    
    if request.method == 'POST':
        nom = medicament.nom
        medicament.delete()
        messages.success(request, f'Médicament "{nom}" supprimé avec succès !')
        return redirect('stock:liste_medicaments')
    
    return render(request, 'stock/medicament_confirm_delete.html', {'medicament': medicament})

@login_required
def export_medicaments_csv(request):
    """Exporter tous les médicaments en CSV - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medicaments_export.csv"'
    
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Nom', 'Code barre', 'Description', 'Prix achat', 'Prix vente', 
                     'Quantité stock', 'Seuil alerte', 'Date expiration', 'Date ajout'])
    
    for med in Medicament.objects.all():
        writer.writerow([
            med.id, med.nom, med.code_barre, med.description,
            med.prix_achat, med.prix_vente, med.quantite_stock,
            med.seuil_alerte, med.date_expiration, med.date_ajout
        ])
    
    messages.success(request, 'Export CSV effectué avec succès !')
    return response

@login_required
def import_medicaments_csv(request):
    """Importer des médicaments depuis un fichier CSV - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Le fichier doit être au format CSV')
            return redirect('stock:import_csv')
        
        decoded_file = TextIOWrapper(csv_file, encoding='utf-8-sig')
        reader = csv.DictReader(decoded_file, delimiter=';')
        
        compteur = 0
        erreurs = []
        
        for row in reader:
            try:
                medicament, created = Medicament.objects.get_or_create(
                    code_barre=row.get('code_barre', ''),
                    defaults={
                        'nom': row.get('nom', ''),
                        'description': row.get('description', ''),
                        'prix_achat': float(row.get('prix_achat', 0)),
                        'prix_vente': float(row.get('prix_vente', 0)),
                        'quantite_stock': int(row.get('quantite_stock', 0)),
                        'seuil_alerte': int(row.get('seuil_alerte', 10)),
                        'date_expiration': row.get('date_expiration', '2025-12-31'),
                    }
                )
                
                if created:
                    compteur += 1
                else:
                    medicament.nom = row.get('nom', medicament.nom)
                    medicament.description = row.get('description', medicament.description)
                    medicament.prix_achat = float(row.get('prix_achat', medicament.prix_achat))
                    medicament.prix_vente = float(row.get('prix_vente', medicament.prix_vente))
                    medicament.quantite_stock = int(row.get('quantite_stock', medicament.quantite_stock))
                    medicament.seuil_alerte = int(row.get('seuil_alerte', medicament.seuil_alerte))
                    medicament.save()
                    compteur += 1
                    
            except Exception as e:
                erreurs.append(f"Erreur ligne {reader.line_num}: {str(e)}")
        
        if erreurs:
            for err in erreurs[:5]:
                messages.error(request, err)
        else:
            messages.success(request, f'✅ Import terminé ! {compteur} médicaments importés/mis à jour.')
        
        return redirect('stock:liste_medicaments')
    
    return render(request, 'stock/import_csv.html')

@login_required
def export_medicaments_excel(request):
    """Exporter tous les médicaments en Excel - Réservé aux pharmaciens et admin"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    medicaments = Medicament.objects.all().values(
        'id', 'nom', 'code_barre', 'description', 'prix_achat', 
        'prix_vente', 'quantite_stock', 'seuil_alerte', 'date_expiration'
    )
    
    df = pd.DataFrame(list(medicaments))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="medicaments_export.xlsx"'
    
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Médicaments', index=False)
    
    return response
# ============================================
# VUES ALERTES
# ============================================

@login_required
def verifier_disponibilite(request):
    """Vérifier la disponibilité des médicaments et envoyer des emails aux fournisseurs si nécessaire"""
    if request.user.profile.role != 'admin':
        messages.error(request, '❌ Accès réservé aux administrateurs')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        messages.warning(request, 'Aucun fournisseur lié aux médicaments dans le modèle actuel. Aucune email n\'a été envoyée.')
        return redirect('stock:verifier_disponibilite')
    
    # GET: Afficher les médicaments disponibles, indisponibles et problématiques
    medicaments_disponibles = Medicament.objects.filter(quantite_stock__gt=0).order_by('nom')
    medicaments_indisponibles = Medicament.objects.filter(quantite_stock=0).order_by('nom')
    medicaments_problematiques = Medicament.objects.filter(
        models.Q(quantite_stock=0) | models.Q(quantite_stock__lte=models.F('seuil_alerte'))
    )
    
    context = {
        'medicaments_disponibles': medicaments_disponibles,
        'medicaments_indisponibles': medicaments_indisponibles,
        'medicaments_problematiques': medicaments_problematiques,
        'total_problemes': medicaments_problematiques.count(),
    }
    
    return render(request, 'stock/verifier_disponibilite.html', context)

@login_required
def alertes_stock(request):
    """Alertes automatiques sur le stock pour pharmaciens"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Médicaments en rupture de stock
    medicaments_rupture = Medicament.objects.filter(quantite_stock=0)
    
    # Médicaments en stock critique (en dessous du seuil)
    medicaments_critique = Medicament.objects.filter(quantite_stock__lte=models.F('seuil_alerte'), quantite_stock__gt=0)
    
    # Médicaments expirant bientôt (dans les 30 jours)
    date_limite = timezone.now().date() + timedelta(days=30)
    medicaments_expirant = Medicament.objects.filter(date_expiration__lte=date_limite, date_expiration__gte=timezone.now().date())
    
    # Médicaments déjà expirés
    medicaments_expires = Medicament.objects.filter(date_expiration__lt=timezone.now().date())
    
    context = {
        'medicaments_rupture': medicaments_rupture,
        'medicaments_critique': medicaments_critique,
        'medicaments_expirant': medicaments_expirant,
        'medicaments_expires': medicaments_expires,
        'total_alertes': medicaments_rupture.count() + medicaments_critique.count() + medicaments_expirant.count() + medicaments_expires.count(),
    }
    
    return render(request, 'stock/alertes.html', context)

# ============================================
# VUES FOURNISSEURS
# ============================================

@login_required
def liste_fournisseurs(request):
    """Liste tous les fournisseurs"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, 'Accès réservé aux administrateurs et pharmaciens')
        return redirect('stock:liste_medicaments')
    
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'stock/fournisseur_liste.html', {'fournisseurs': fournisseurs})

@login_required
def ajouter_fournisseur(request):
    """Ajouter un fournisseur"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Accès réservé aux administrateurs')
        return redirect('stock:liste_fournisseurs')
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'✅ Fournisseur "{fournisseur.nom}" ajouté avec succès !')
            return redirect('stock:liste_fournisseurs')
        else:
            messages.error(request, 'Erreur dans le formulaire')
    else:
        form = FournisseurForm()
    
    return render(request, 'stock/fournisseur_form.html', {'form': form, 'titre': 'Ajouter un fournisseur'})

@login_required
def modifier_fournisseur(request, pk):
    """Modifier un fournisseur"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Accès réservé aux administrateurs')
        return redirect('stock:liste_fournisseurs')
    
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Fournisseur "{fournisseur.nom}" modifié avec succès !')
            return redirect('stock:liste_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)
    
    return render(request, 'stock/fournisseur_form.html', {'form': form, 'titre': 'Modifier le fournisseur'})

@login_required
def supprimer_fournisseur(request, pk):
    """Supprimer un fournisseur"""
    if request.user.profile.role != 'admin':
        messages.error(request, 'Accès réservé aux administrateurs')
        return redirect('stock:liste_fournisseurs')
    
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        nom = fournisseur.nom
        fournisseur.delete()
        messages.success(request, f'✅ Fournisseur "{nom}" supprimé avec succès !')
        return redirect('stock:liste_fournisseurs')
    
    return render(request, 'stock/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})

@login_required
def envoyer_email_fournisseur(request, pk):
    """Envoyer un email à un fournisseur"""
    if request.user.profile.role not in ['admin', 'pharmacien']:
        messages.error(request, 'Accès réservé')
        return redirect('stock:liste_medicaments')
    
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    
    if request.method == 'POST':
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')
        
        if sujet and message:
            try:
                send_mail(
                    f"[Pharmacie H.I.B] {sujet}",
                    f"Bonjour {fournisseur.contact_nom},\n\n{message}\n\nCordialement,\nPharmacie H.I.B",
                    settings.DEFAULT_FROM_EMAIL,
                    [fournisseur.email],
                    fail_silently=False,
                )
                messages.success(request, f'📧 Email envoyé à {fournisseur.nom}')
            except Exception as e:
                messages.error(request, f'Erreur d\'envoi: {str(e)}')
        else:
            messages.error(request, 'Veuillez remplir tous les champs')
        
        return redirect('stock:liste_fournisseurs')
    
    return render(request, 'stock/fournisseur_email.html', {'fournisseur': fournisseur})


def about(request):
    """Page À propos avec nos valeurs - Accès public"""
    return render(request, 'about.html')