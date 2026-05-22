from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password_request'),
    path('reset-password/<str:uid>/<str:token>/', views.forgot_password_reset, name='forgot_password_reset'),
]