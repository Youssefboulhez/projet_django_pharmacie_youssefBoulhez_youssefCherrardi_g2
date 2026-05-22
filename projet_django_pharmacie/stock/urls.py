from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogue/', views.liste_medicaments, name='liste_medicaments'),
    path('recherche/', views.rechercher_medicaments, name='recherche'),
    path('ajouter/', views.ajouter_medicament, name='ajouter'),
    path('<int:pk>/modifier/', views.modifier_medicament, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_medicament, name='supprimer'),
    path('export/csv/', views.export_medicaments_csv, name='export_csv'),
    path('export/excel/', views.export_medicaments_excel, name='export_excel'),
    path('import/csv/', views.import_medicaments_csv, name='import_csv'),
    
    # URLs Fournisseurs
    path('alertes/', views.alertes_stock, name='alertes'),
    path('verifier-disponibilite/', views.verifier_disponibilite, name='verifier_disponibilite'),
    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur, name='ajouter_fournisseur'),
    path('fournisseurs/<int:pk>/modifier/', views.modifier_fournisseur, name='modifier_fournisseur'),
    path('fournisseurs/<int:pk>/supprimer/', views.supprimer_fournisseur, name='supprimer_fournisseur'),
    path('fournisseurs/<int:pk>/email/', views.envoyer_email_fournisseur, name='email_fournisseur'),
    path('about/', views.about, name='about'),
]