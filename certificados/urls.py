from django.urls import path
from . import views

app_name = 'certificados'

urlpatterns = [
    # Categorías
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_lista'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_nueva'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    # Certificados
    path('certificados/', views.CertificadoListView.as_view(), name='certificado_lista'),
    path('certificados/nuevo/', views.CertificadoCreateView.as_view(), name='certificado_nuevo'),
    path('certificados/<int:pk>/editar/', views.CertificadoUpdateView.as_view(), name='certificado_editar'),
    path('certificados/<int:pk>/eliminar/', views.CertificadoDeleteView.as_view(), name='certificado_eliminar'),
    path('certificados/<int:pk>/descargar/', views.CertificadoDownloadView.as_view(), name='certificado_descargar'),

]
