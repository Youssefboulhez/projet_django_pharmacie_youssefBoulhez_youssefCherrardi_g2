from django.db import models
from django.urls import reverse
from datetime import date
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class Medicament(models.Model):
    """Modèle représentant un médicament en stock"""
    
    # Informations générales
    code_barre = models.CharField(max_length=50, unique=True, verbose_name="Code barre")
    nom = models.CharField(max_length=200, verbose_name="Nom du médicament")
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Informations pharmaceutiques
    dosage = models.CharField(max_length=100, blank=True, verbose_name="Dosage (ex: 500mg)")
    forme = models.CharField(max_length=100, blank=True, verbose_name="Forme (comprimé, sirop, etc.)")
    
    # Prix et stock
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix d'achat")
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix de vente")
    quantite_stock = models.IntegerField(default=0, verbose_name="Quantité en stock")
    seuil_alerte = models.IntegerField(default=10, verbose_name="Seuil d'alerte")
    
    # Métadonnées
    image = models.ImageField(upload_to='medicaments/', null=True, blank=True, verbose_name="Image")
    date_expiration = models.DateField(verbose_name="Date d'expiration")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    
    def __str__(self):
        return f"{self.nom} ({self.code_barre})"
    
    def get_absolute_url(self):
        return reverse('stock:medicament_detail', args=[str(self.id)])
    
    def est_en_stock_insuffisant(self):
        """Vérifie si le stock est en dessous du seuil d'alerte"""
        return self.quantite_stock <= self.seuil_alerte
    
    def est_expire(self):
        """Vérifie si le médicament est expiré"""
        return self.date_expiration < date.today()
    
    def est_proche_expiration(self, jours=30):
        """Vérifie si le médicament expire bientôt (défaut: 30 jours)"""
        delta = self.date_expiration - date.today()
        return 0 < delta.days <= jours
    
    def est_achetable(self):
        """Vérifie si le médicament peut être vendu (non expiré ET stock > 0)"""
        return not self.est_expire() and self.quantite_stock > 0
    
    def jours_avant_expiration(self):
        """Retourne le nombre de jours avant expiration (négatif si expiré)"""
        delta = self.date_expiration - date.today()
        return delta.days
    
    def statut_stock(self):
        """Retourne le statut du stock"""
        if self.quantite_stock == 0:
            return 'rupture'
        elif self.quantite_stock <= self.seuil_alerte:
            return 'critique'
        else:
            return 'normal'
    
    class Meta:
        verbose_name = "Médicament"
        verbose_name_plural = "Médicaments"
        ordering = ['nom']


class Fournisseur(models.Model):
    """Modèle pour la gestion des fournisseurs"""
    
    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom du fournisseur")
    code_fournisseur = models.CharField(max_length=50, unique=True, verbose_name="Code fournisseur")
    
    # Contact principal
    email = models.EmailField(verbose_name="Email professionnel")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    telephone_secondaire = models.CharField(max_length=20, blank=True, verbose_name="Téléphone secondaire")
    
    # Adresse
    adresse = models.TextField(verbose_name="Adresse")
    ville = models.CharField(max_length=100, verbose_name="Ville")
    code_postal = models.CharField(max_length=10, verbose_name="Code postal")
    pays = models.CharField(max_length=50, default="Maroc", verbose_name="Pays")
    
    # Contact commercial
    contact_nom = models.CharField(max_length=100, verbose_name="Nom du contact")
    
    # Catégorie de produits
    categorie_produits = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Catégories de produits",
        help_text="Ex: Antibiotiques, Paracétamol, etc."
    )
    
    # Délais et conditions
    delai_livraison = models.IntegerField(default=3, verbose_name="Délai de livraison (jours)")
    conditions_paiement = models.TextField(blank=True, verbose_name="Conditions de paiement")
    
    # Statut
    actif = models.BooleanField(default=True, verbose_name="Fournisseur actif")
    note = models.TextField(blank=True, verbose_name="Notes internes")
    
    # Métadonnées
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    def __str__(self):
        return f"{self.nom} ({self.code_fournisseur})"
    
    def get_absolute_url(self):
        return reverse('stock:fournisseur_detail', args=[str(self.id)])
    
    def envoyer_email(self, sujet, message):
        """Envoyer un email professionnel au fournisseur"""
        try:
            send_mail(
                sujet,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            return False
    
    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']