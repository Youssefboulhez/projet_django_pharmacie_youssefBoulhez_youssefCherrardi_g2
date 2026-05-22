from django.db import models
from django.contrib.auth.models import User
from stock.models import Medicament

class Vente(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    PAIEMENT_CHOICES = [
        ('carte', 'Paiement par carte'),
        ('livraison', 'Paiement à la livraison'),
        ('effectue', 'Paiement effectué'),
        ('en_attente', 'Paiement en attente'),
    ]
    
    numero_facture = models.CharField(max_length=50, unique=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_vente = models.DateTimeField(auto_now_add=True)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    mode_paiement = models.CharField(max_length=20, choices=PAIEMENT_CHOICES, default='livraison')
    
    class Meta:
        ordering = ['-date_vente']
    
    def __str__(self):
        return f"Facture {self.numero_facture} - {self.date_vente.strftime('%d/%m/%Y')}"


class DetailVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='details')
    medicament = models.ForeignKey(Medicament, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
    
    def __str__(self):
        return f"{self.medicament.nom} x {self.quantite}"