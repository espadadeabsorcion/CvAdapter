"""
URL configuration for cv_adaptable_project project.
"""
from django.contrib import admin
from django.urls import path, include
import generador.views as generador_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Raíz: la página de inicio es el CV público
    path('', generador_views.CVPublicoView.as_view(), name='root'),
    # Core: login, logout, dashboard
    path('', include('core.urls')),
    # Perfil: perfil personal, experiencia, educación, habilidades, idiomas
    path('perfil/', include('perfil.urls')),
    # Certificados & Categorías
    path('', include('certificados.urls')),
    # Generador de CV adaptado
    # Las rutas públicas del CV van ANTES del include('generador.urls') para
    # garantizar su prioridad en la resolución de URLs.
    path('cv/publico/', generador_views.CVPublicoView.as_view(), name='cv_publico_por_defecto'),
    path('cv/publico/<str:username>/', generador_views.CVPublicoView.as_view(), name='cv_publico'),
    path('cv/', include('generador.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


