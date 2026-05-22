from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.utils import timezone
from datetime import date
from stock.models import Medicament
from .models import Vente, DetailVente
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse
import io
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

@login_required
def panier(request):
    """Afficher le panier avec vérification des produits expirés"""
    panier = request.session.get('panier', {})
    articles = []
    total = 0
    panier_modifie = False
    
    for medicament_id, quantite in list(panier.items()):
        medicament = get_object_or_404(Medicament, pk=medicament_id)
        
        if medicament.est_expire():
            messages.warning(request, f'⚠️ "{medicament.nom}" a été retiré du panier car il est EXPIRÉ')
            del panier[medicament_id]
            panier_modifie = True
            continue
        
        if quantite > medicament.quantite_stock:
            messages.warning(request, f'⚠️ Stock insuffisant pour "{medicament.nom}". Quantité ajustée de {quantite} à {medicament.quantite_stock}')
            quantite = medicament.quantite_stock
            if quantite <= 0:
                del panier[medicament_id]
            else:
                panier[medicament_id] = quantite
            panier_modifie = True
        
        sous_total = medicament.prix_vente * quantite
        total += sous_total
        articles.append({
            'medicament': medicament,
            'quantite': quantite,
            'sous_total': sous_total
        })
    
    if panier_modifie:
        request.session['panier'] = panier
    
    return render(request, 'ventes/panier.html', {
        'articles': articles,
        'total': total
    })

@login_required
def ajouter_au_panier(request, pk):
    """Ajouter un médicament au panier avec vérifications"""
    medicament = get_object_or_404(Medicament, pk=pk)
    
    if medicament.est_expire():
        messages.error(request, f'❌ "{medicament.nom}" est EXPIRÉ depuis le {medicament.date_expiration.strftime("%d/%m/%Y")}. Vente impossible !')
        return redirect('stock:liste_medicaments')
    
    if medicament.quantite_stock <= 0:
        messages.error(request, f'❌ "{medicament.nom}" est en RUPTURE DE STOCK !')
        return redirect('stock:liste_medicaments')
    
    panier = request.session.get('panier', {})
    medicament_id = str(pk)
    
    if medicament_id in panier:
        nouvelle_quantite = panier[medicament_id] + 1
        if nouvelle_quantite > medicament.quantite_stock:
            messages.warning(request, f'⚠️ Stock insuffisant pour "{medicament.nom}". Maximum disponible: {medicament.quantite_stock}')
            return redirect('stock:liste_medicaments')
        panier[medicament_id] = nouvelle_quantite
    else:
        panier[medicament_id] = 1
    
    request.session['panier'] = panier
    
    if medicament.est_proche_expiration():
        messages.warning(request, f'⚠️ Attention : "{medicament.nom}" expire dans {medicament.jours_avant_expiration()} jours !')
    else:
        messages.success(request, f'✅ "{medicament.nom}" ajouté au panier')
    
    return redirect('stock:liste_medicaments')

@login_required
def retirer_du_panier(request, pk):
    """Retirer un médicament du panier"""
    medicament = get_object_or_404(Medicament, pk=pk)
    panier = request.session.get('panier', {})
    medicament_id = str(pk)
    
    if medicament_id in panier:
        if panier[medicament_id] > 1:
            panier[medicament_id] -= 1
            messages.success(request, f'Quantité réduite pour "{medicament.nom}"')
        else:
            del panier[medicament_id]
            messages.success(request, f'"{medicament.nom}" retiré du panier')
    
    request.session['panier'] = panier
    return redirect('ventes:panier')

@login_required
def valider_commande(request):
    """Valider la commande avec choix du mode de paiement"""
    panier = request.session.get('panier', {})
    
    if not panier:
        messages.error(request, 'Votre panier est vide')
        return redirect('ventes:panier')
    
    if request.method == 'POST':
        mode_paiement = request.POST.get('mode_paiement', 'livraison')
        
        erreurs = []
        for medicament_id, quantite in panier.items():
            medicament = get_object_or_404(Medicament, pk=medicament_id)
            if medicament.est_expire():
                erreurs.append(f'❌ {medicament.nom} - EXPIRÉ')
            elif quantite > medicament.quantite_stock:
                erreurs.append(f'⚠️ {medicament.nom} - Stock insuffisant')
        
        if erreurs:
            for erreur in erreurs:
                messages.error(request, erreur)
            return redirect('ventes:panier')
        
        numero_facture = f"FAC-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        vente = Vente.objects.create(
            numero_facture=numero_facture,
            utilisateur=request.user,
            statut='terminee',
            mode_paiement=mode_paiement
        )
        
        total = 0
        for medicament_id, quantite in panier.items():
            medicament = Medicament.objects.get(pk=medicament_id)
            
            DetailVente.objects.create(
                vente=vente,
                medicament=medicament,
                quantite=quantite,
                prix_unitaire=medicament.prix_vente
            )
            
            medicament.quantite_stock -= quantite
            medicament.save()
            total += medicament.prix_vente * quantite
            
            if medicament.est_en_stock_insuffisant():
                messages.warning(request, f'⚠️ Stock critique pour "{medicament.nom}". Il reste {medicament.quantite_stock} unités.')
        
        vente.total_ttc = total
        vente.save()
        
        request.session['panier'] = {}
        
        # Générer le PDF pour l'email
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "PHARMAGEST")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(width - 150, height - 70, "FACTURE")
        c.setFont("Helvetica", 10)
        c.drawString(width - 150, height - 85, f"N°: {vente.numero_facture}")
        c.drawString(width - 150, height - 100, f"Date: {vente.date_vente.strftime('%d/%m/%Y %H:%M')}")
        
        c.line(50, height - 120, width - 50, height - 120)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 145, "Client:")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 160, f"Nom: {vente.utilisateur.username}")
        c.drawString(50, height - 175, f"Email: {vente.utilisateur.email}")
        
        y = height - 230
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Désignation")
        c.drawString(300, y, "Qté")
        c.drawString(370, y, "Prix U.")
        c.drawString(450, y, "Total")
        c.line(50, y - 5, width - 50, y - 5)
        
        c.setFont("Helvetica", 9)
        y -= 25
        total_pdf = 0
        
        for detail in vente.details.all():
            c.drawString(50, y, detail.medicament.nom[:40])
            c.drawString(300, y, str(detail.quantite))
            c.drawString(370, y, f"{detail.prix_unitaire:.2f} DH")
            sous_total = detail.quantite * detail.prix_unitaire
            c.drawString(450, y, f"{sous_total:.2f} DH")
            total_pdf += sous_total
            y -= 20
            
            if y < 100:
                c.showPage()
                y = height - 50
        
        c.line(50, y - 5, width - 50, y - 5)
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(370, y, "TOTAL TTC:")
        c.drawString(450, y, f"{total_pdf:.2f} DH")
        c.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        try:
            envoyer_email_confirmation(vente, pdf_content)
            messages.success(request, f'✅ Commande validée ! Un email a été envoyé à {vente.utilisateur.email}')
        except Exception as e:
            messages.success(request, f'✅ Commande validée ! Facture: {numero_facture}')
        
        return redirect('ventes:facture', pk=vente.pk)
    
    # GET: Afficher le formulaire de validation avec choix du paiement
    articles = []
    total = 0
    for medicament_id, quantite in panier.items():
        medicament = get_object_or_404(Medicament, pk=medicament_id)
        sous_total = medicament.prix_vente * quantite
        total += sous_total
        articles.append({
            'medicament': medicament,
            'quantite': quantite,
            'sous_total': sous_total
        })
    
    return render(request, 'ventes/valider_commande.html', {
        'articles': articles,
        'total': total
    })

@login_required
def facture(request, pk):
    """Afficher la facture"""
    vente = get_object_or_404(Vente, pk=pk)
    return render(request, 'ventes/facture.html', {'vente': vente})

@login_required
def historique_ventes(request):
    """Historique des ventes"""
    ventes = Vente.objects.filter(utilisateur=request.user).order_by('-date_vente')
    return render(request, 'ventes/historique.html', {'ventes': ventes})

@login_required
def export_pdf_facture(request, pk):
    """Exporter la facture en PDF"""
    vente = get_object_or_404(Vente, pk=pk)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{vente.numero_facture}.pdf"'
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "PHARMAGEST")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "123 Rue de la Pharmacie")
    c.drawString(50, height - 85, "75001 Paris")
    c.drawString(50, height - 100, "Tel: 01 23 45 67 89")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(width - 150, height - 70, "FACTURE")
    c.setFont("Helvetica", 10)
    c.drawString(width - 150, height - 85, f"N°: {vente.numero_facture}")
    c.drawString(width - 150, height - 100, f"Date: {vente.date_vente.strftime('%d/%m/%Y %H:%M')}")
    
    c.line(50, height - 120, width - 50, height - 120)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 145, "Client:")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 160, f"Nom: {vente.utilisateur.username}")
    c.drawString(50, height - 175, f"Email: {vente.utilisateur.email}")
    
    y = height - 230
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Désignation")
    c.drawString(300, y, "Qté")
    c.drawString(370, y, "Prix U.")
    c.drawString(450, y, "Total")
    c.line(50, y - 5, width - 50, y - 5)
    
    c.setFont("Helvetica", 9)
    y -= 25
    total = 0
    
    for detail in vente.details.all():
        c.drawString(50, y, detail.medicament.nom[:40])
        c.drawString(300, y, str(detail.quantite))
        c.drawString(370, y, f"{detail.prix_unitaire:.2f} DH")
        sous_total = detail.quantite * detail.prix_unitaire
        c.drawString(450, y, f"{sous_total:.2f} DH")
        total += sous_total
        y -= 20
        
        if y < 100:
            c.showPage()
            y = height - 50
    
    c.line(50, y - 5, width - 50, y - 5)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(370, y, "TOTAL TTC:")
    c.drawString(450, y, f"{total:.2f} DH")
    
    c.setFont("Helvetica", 8)
    c.drawString(50, 50, "Merci de votre confiance - Règlement à réception")
    c.drawString(width - 150, 50, f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    c.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def envoyer_email_confirmation(vente, pdf_content):
    """Envoyer un email de confirmation avec facture PDF"""
    subject = f'Confirmation de commande - {vente.numero_facture}'
    
    html_message = render_to_string('ventes/email_confirmation.html', {
        'vente': vente,
        'client': vente.utilisateur.username,
    })
    plain_message = strip_tags(html_message)
    
    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [vente.utilisateur.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.attach(f'facture_{vente.numero_facture}.pdf', pdf_content, 'application/pdf')
    email.send()

@login_required
def caisse(request):
    """Interface de caisse avec recherche rapide et panier"""
    produits_populaires = Medicament.objects.filter(quantite_stock__gt=0).order_by('-quantite_stock')[:12]
    
    panier = request.session.get('panier', {})
    articles = []
    total = 0
    
    for medicament_id, quantite in panier.items():
        medicament = get_object_or_404(Medicament, pk=medicament_id)
        sous_total = medicament.prix_vente * quantite
        total += sous_total
        articles.append({
            'medicament': medicament,
            'quantite': quantite,
            'sous_total': sous_total
        })
    
    context = {
        'produits_populaires': produits_populaires,
        'articles': articles,
        'total': total,
    }
    return render(request, 'ventes/caisse.html', context)

@login_required
def caisse_pharmacien(request):
    """Interface de caisse spécifique pour pharmacien"""
    if request.user.profile.role not in ['pharmacien', 'admin']:
        messages.error(request, '❌ Accès réservé aux pharmaciens')
        return redirect('stock:liste_medicaments')
    
    # Get today's date
    today = date.today()
    
    # Get today's sales
    ventes_jour = Vente.objects.filter(
        date_vente__date=today,
        statut='terminee'
    ).order_by('-date_vente')
    
    # Calculate total sales for today
    total_ventes_jour = sum(vente.total_ttc for vente in ventes_jour)
    
    # Get popular products (keep this for the left side)
    produits_populaires = Medicament.objects.filter(quantite_stock__gt=0).order_by('-quantite_stock')[:12]
    
    context = {
        'produits_populaires': produits_populaires,
        'ventes_jour': ventes_jour,
        'total_ventes_jour': total_ventes_jour,
        'date_jour': today,
    }
    return render(request, 'ventes/caisse_pharmacien.html', context)

@login_required
def historique_complet(request):
    """Historique complet de toutes les ventes pour les pharmaciens"""
    if request.user.profile.role not in ['pharmacien', 'admin']:
        messages.error(request, '❌ Accès réservé aux pharmaciens et administrateurs')
        return redirect('stock:liste_medicaments')
    
    # Récupérer toutes les ventes terminées
    ventes = Vente.objects.filter(statut='terminee').order_by('-date_vente')
    
    # Calculer le total général
    total_general = sum(vente.total_ttc for vente in ventes)
    
    context = {
        'ventes': ventes,
        'total_general': total_general,
        'titre': 'Historique complet des ventes'
    }
    return render(request, 'ventes/historique_complet.html', context)