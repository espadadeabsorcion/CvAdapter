from django.urls import path
from . import views

app_name = 'perfil'

urlpatterns = [
    # Perfil base
    path('', views.PerfilView.as_view(), name='perfil_detalle'),

    # Experiencia
    path('experiencia/', views.ExperienciaListView.as_view(), name='experiencia_lista'),
    path('experiencia/nueva/', views.ExperienciaCreateView.as_view(), name='experiencia_nueva'),
    path('experiencia/<int:pk>/editar/', views.ExperienciaUpdateView.as_view(), name='experiencia_editar'),
    path('experiencia/<int:pk>/eliminar/', views.ExperienciaDeleteView.as_view(), name='experiencia_eliminar'),

    # Educación
    path('educacion/', views.EducacionListView.as_view(), name='educacion_lista'),
    path('educacion/nueva/', views.EducacionCreateView.as_view(), name='educacion_nueva'),
    path('educacion/<int:pk>/editar/', views.EducacionUpdateView.as_view(), name='educacion_editar'),
    path('educacion/<int:pk>/eliminar/', views.EducacionDeleteView.as_view(), name='educacion_eliminar'),

    # Habilidades
    path('habilidades/', views.HabilidadListView.as_view(), name='habilidad_lista'),
    path('habilidades/nueva/', views.HabilidadCreateView.as_view(), name='habilidad_nueva'),
    path('habilidades/<int:pk>/editar/', views.HabilidadUpdateView.as_view(), name='habilidad_editar'),
    path('habilidades/<int:pk>/eliminar/', views.HabilidadDeleteView.as_view(), name='habilidad_eliminar'),

    # Idiomas
    path('idiomas/', views.IdiomaListView.as_view(), name='idioma_lista'),
    path('idiomas/nuevo/', views.IdiomaCreateView.as_view(), name='idioma_nuevo'),
    path('idiomas/<int:pk>/editar/', views.IdiomaUpdateView.as_view(), name='idioma_editar'),
    path('idiomas/<int:pk>/eliminar/', views.IdiomaDeleteView.as_view(), name='idioma_eliminar'),
]
