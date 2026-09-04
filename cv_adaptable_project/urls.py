"""
URL configuration for cv_adaptable_project project.
"""
from django.contrib import admin
from django.urls import path, include
from core.views import RootRedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Raíz: redirige según estado de sesión
    path('', RootRedirectView.as_view(), name='root'),
    # Core: login, logout, dashboard
    path('', include('core.urls')),
    # Perfil: perfil personal, experiencia, educación, habilidades, idiomas
    path('perfil/', include('perfil.urls')),
    # Certificados & Categorías
    path('', include('certificados.urls')),
    # Generador de CV adaptado
    path('cv/', include('generador.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


