from stock.models import Medicament
from django.utils import timezone
from datetime import timedelta

def alertes_context(request):
    """Ajoute le nombre total d'alertes au contexte"""
    if request.user.is_authenticated and request.user.profile.role in ['admin', 'pharmacien']:
        # Médicaments en rupture
        rupture = Medicament.objects.filter(quantite_stock=0).count()
        
        # Stock critique
        critique = Medicament.objects.filter(quantite_stock__lte=Medicament.objects.values('seuil_alerte')).count()
        
        # Expiration proche
        date_limite = timezone.now().date() + timedelta(days=30)
        expirant = Medicament.objects.filter(date_expiration__lte=date_limite, date_expiration__gte=timezone.now().date()).count()
        
        # Expirés
        expires = Medicament.objects.filter(date_expiration__lt=timezone.now().date()).count()
        
        total_alertes = rupture + critique + expirant + expires
    else:
        total_alertes = 0
    
    return {'total_alertes': total_alertes}