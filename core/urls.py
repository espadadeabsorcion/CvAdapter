from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'core'

urlpatterns = [
    # Autenticación y Dashboard
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # Auto-registro y eliminación de cuenta propia
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    path('eliminar-cuenta/', views.EliminarCuentaPropiaView.as_view(), name='eliminar_cuenta'),

    # CRUD de Usuarios (Staff / Administrador)
    path('gestion/usuarios/', views.UsuarioAdminListView.as_view(), name='admin_usuario_lista'),
    path('gestion/usuarios/nuevo/', views.UsuarioAdminCreateView.as_view(), name='admin_usuario_nuevo'),
    path('gestion/usuarios/<int:pk>/editar/', views.UsuarioAdminUpdateView.as_view(), name='admin_usuario_editar'),
    path('gestion/usuarios/<int:pk>/eliminar/', views.UsuarioAdminDeleteView.as_view(), name='admin_usuario_eliminar'),
    path('gestion/usuarios/<int:pk>/toggle-active/', views.UsuarioAdminToggleActiveView.as_view(), name='admin_usuario_toggle_active'),
]
