from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_admin, name='index'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),      # ← nouveau
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'), # ← nouveau
]