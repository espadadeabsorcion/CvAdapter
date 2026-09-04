from django.urls import path
from . import views

app_name = 'generador'

urlpatterns = [
    path('generar/', views.SeleccionarCategoriaView.as_view(), name='seleccionar_categorias'),
    path('cv/', views.GenerarCvView.as_view(), name='cv_adaptado'),
    path('preview/', views.PreviewCvView.as_view(), name='cv_preview'),
]
