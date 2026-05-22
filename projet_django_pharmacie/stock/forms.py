from django import forms
from .models import Medicament, Fournisseur

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = [
            'code_barre', 'nom', 'description', 
            'prix_achat', 'prix_vente', 'quantite_stock', 
            'seuil_alerte', 'image', 'date_expiration'
        ]
        widgets = {
            'code_barre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234567890123'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Paracétamol 500mg'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du médicament...'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantite_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'seuil_alerte': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'code_barre': 'Code barre',
            'nom': 'Nom du médicament',
            'description': 'Description',
            'prix_achat': "Prix d'achat (DH)",
            'prix_vente': 'Prix de vente (DH)',
            'quantite_stock': 'Quantité en stock',
            'seuil_alerte': "Seuil d'alerte",
            'image': 'Image du médicament',
            'date_expiration': "Date d'expiration",
        }

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = '__all__'
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'code_fournisseur': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone_secondaire': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'categorie_produits': forms.TextInput(attrs={'class': 'form-control'}),
            'delai_livraison': forms.NumberInput(attrs={'class': 'form-control'}),
            'conditions_paiement': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }