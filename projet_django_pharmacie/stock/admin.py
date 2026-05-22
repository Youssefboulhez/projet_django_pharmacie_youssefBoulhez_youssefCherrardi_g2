from django.contrib import admin
from .models import Medicament, Fournisseur

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_barre', 'prix_vente', 'quantite_stock', 'date_expiration')
    list_filter = ('date_expiration', 'seuil_alerte')
    search_fields = ('nom', 'code_barre')
    list_editable = ('prix_vente', 'quantite_stock')
    fieldsets = (
        ('Informations générales', {
            'fields': ('code_barre', 'nom', 'description', 'image')
        }),
        ('Prix et stock', {
            'fields': ('prix_achat', 'prix_vente', 'quantite_stock', 'seuil_alerte')
        }),
        ('Dates', {
            'fields': ('date_expiration',)
        }),
    )

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_fournisseur', 'email', 'telephone', 'ville', 'actif')
    list_filter = ('actif', 'ville', 'pays')
    search_fields = ('nom', 'code_fournisseur', 'email')