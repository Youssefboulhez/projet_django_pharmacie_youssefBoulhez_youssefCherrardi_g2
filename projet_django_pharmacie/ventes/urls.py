from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('panier/', views.panier, name='panier'),
    path('ajouter/<int:pk>/', views.ajouter_au_panier, name='ajouter'),
    path('retirer/<int:pk>/', views.retirer_du_panier, name='retirer'),
    path('valider/', views.valider_commande, name='valider'),
    path('facture/<int:pk>/', views.facture, name='facture'),
    path('facture/<int:pk>/pdf/', views.export_pdf_facture, name='facture_pdf'),
    path('historique/', views.historique_ventes, name='historique'),
    path('historique/complet/', views.historique_complet, name='historique_complet'),
    path('caisse/', views.caisse, name='caisse'), 
    path('caisse/pharmacien/', views.caisse_pharmacien, name='caisse_pharmacien'),
]