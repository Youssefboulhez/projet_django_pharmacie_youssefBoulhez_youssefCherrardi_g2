from django.contrib import admin
from .models import Vente, DetailVente

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'utilisateur', 'date_vente', 'total_ttc', 'statut', 'mode_paiement')
    list_filter = ('statut', 'mode_paiement')
    search_fields = ('numero_facture',)

@admin.register(DetailVente)
class DetailVenteAdmin(admin.ModelAdmin):
    list_display = ('vente', 'medicament', 'quantite', 'prix_unitaire')