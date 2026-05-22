from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='stock:home'), name='logout'),
    path('register/', user_views.register, name='register'),
    path('', include('stock.urls')),
    path('users/', include('users.urls')),
    path('ventes/', include('ventes.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)