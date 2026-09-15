from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView

from .forms import (
    EliminarCuentaPropiaForm,
    RegistroUsuarioForm,
    UsuarioAdminCreateForm,
    UsuarioAdminUpdateForm,
)


def eliminar_usuario_y_archivos(user: User):
    """
    Elimina un usuario, sus archivos físicos de certificados en disco,
    su foto de perfil y todos los modelos en cascada.
    """
    from certificados.models import Certificado
    from certificados.file_handler import CertificadoFileHandler

    # 1. Eliminar archivos de certificados
    certificados = Certificado.objects.filter(perfil__usuario=user)
    for cert in certificados:
        try:
            CertificadoFileHandler.delete_file(cert)
        except Exception:
            pass

    # 2. Eliminar fotografía de perfil en disco si existe
    if hasattr(user, 'perfil') and user.perfil.foto:
        try:
            user.perfil.foto.delete(save=False)
        except Exception:
            pass

    # 3. Eliminar usuario (Django elimina Perfil, Certificado, etc. por CASCADE)
    user.delete()


class CustomLoginView(LoginView):
    """
    LoginView personalizada que muestra un mensaje genérico en caso de
    credenciales inválidas, sin revelar si fue el usuario o la contraseña
    lo que falló (Req. 1.2).
    """
    template_name = 'core/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        form.errors.clear()
        form.add_error(None, 'Usuario o contraseña incorrectos.')
        return super().form_invalid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard principal. Requiere sesión activa; de lo contrario redirige
    a /login/ preservando la URL solicitada como parámetro next (Req. 1.5).
    """
    template_name = 'core/dashboard.html'


class RootRedirectView(View):
    """
    Vista de conveniencia para redirección raíz (si se usa).
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return redirect('core:login')


# =============================================================================
# Auto-registro y Gestión de Cuenta Propia por el Usuario
# =============================================================================

class RegistroUsuarioView(View):
    """
    Permite a nuevos usuarios registrarse de forma pública.
    Crea el usuario y su perfil base, e inicia sesión automáticamente.
    """
    template_name = 'core/registro.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = RegistroUsuarioForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'¡Bienvenido {user.get_full_name() or user.username}! Tu cuenta y perfil base han sido creados.')
            return redirect('perfil:perfil_detalle')
        return render(request, self.template_name, {'form': form})


class EliminarCuentaPropiaView(LoginRequiredMixin, View):
    """
    Permite a un usuario autenticado eliminar su propia cuenta permanentemente,
    incluyendo su perfil, certificados, habilidades y archivos adjuntos.
    """
    template_name = 'core/eliminar_cuenta.html'

    def get(self, request, *args, **kwargs):
        form = EliminarCuentaPropiaForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = EliminarCuentaPropiaForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            username = user.username
            logout(request)
            eliminar_usuario_y_archivos(user)
            messages.info(request, f'La cuenta de @{username} y todos sus datos han sido eliminados permanentemente.')
            return redirect('root')
        return render(request, self.template_name, {'form': form})


# =============================================================================
# CRUD de Usuarios para Administradores (Staff / Superusuarios)
# =============================================================================

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe el acceso exclusivamente a usuarios con rol staff o superusuario."""
    raise_exception = True

    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )


class UsuarioAdminListView(StaffRequiredMixin, ListView):
    """Listado de todos los usuarios registrados en el sistema."""
    model = User
    template_name = 'core/admin/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 25

    def get_queryset(self):
        return User.objects.select_related('perfil').order_by('-date_joined')


class UsuarioAdminCreateView(StaffRequiredMixin, View):
    """Creación de un nuevo usuario desde el panel de administración."""
    template_name = 'core/admin/usuario_form.html'

    def get(self, request, *args, **kwargs):
        form = UsuarioAdminCreateForm()
        return render(request, self.template_name, {'form': form, 'es_edicion': False})

    def post(self, request, *args, **kwargs):
        form = UsuarioAdminCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario @{user.username} creado correctamente.')
            return redirect('core:admin_usuario_lista')
        return render(request, self.template_name, {'form': form, 'es_edicion': False})


class UsuarioAdminUpdateView(StaffRequiredMixin, View):
    """Edición de un usuario existente desde el panel de administración."""
    template_name = 'core/admin/usuario_form.html'

    def get(self, request, pk, *args, **kwargs):
        usuario = get_object_or_404(User, pk=pk)
        form = UsuarioAdminUpdateForm(instance=usuario)
        return render(request, self.template_name, {'form': form, 'usuario_obj': usuario, 'es_edicion': True})

    def post(self, request, pk, *args, **kwargs):
        usuario = get_object_or_404(User, pk=pk)
        form = UsuarioAdminUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario @{usuario.username} actualizado correctamente.')
            return redirect('core:admin_usuario_lista')
        return render(request, self.template_name, {'form': form, 'usuario_obj': usuario, 'es_edicion': True})


class UsuarioAdminDeleteView(StaffRequiredMixin, View):
    """Eliminación de un usuario y sus recursos desde el panel de administración."""
    template_name = 'core/admin/usuario_confirm_delete.html'

    def get(self, request, pk, *args, **kwargs):
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.error(request, "No puedes eliminar tu propia cuenta desde este panel. Usa la opción 'Eliminar mi cuenta'.")
            return redirect('core:admin_usuario_lista')
        return render(request, self.template_name, {'usuario_obj': usuario})

    def post(self, request, pk, *args, **kwargs):
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.error(request, "No puedes eliminar tu propia cuenta desde el panel de administración.")
            return redirect('core:admin_usuario_lista')
        username = usuario.username
        eliminar_usuario_y_archivos(usuario)
        messages.success(request, f'Usuario @{username} y todos sus datos han sido eliminados.')
        return redirect('core:admin_usuario_lista')


class UsuarioAdminToggleActiveView(StaffRequiredMixin, View):
    """Activa o suspende rápidamente a un usuario."""
    def post(self, request, pk, *args, **kwargs):
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.error(request, "No puedes suspender tu propia cuenta.")
            return redirect('core:admin_usuario_lista')

        usuario.is_active = not usuario.is_active
        usuario.save()

        if hasattr(usuario, 'perfil'):
            usuario.perfil.is_active = usuario.is_active
            usuario.perfil.save()

        estado = "activada" if usuario.is_active else "suspendida"
        messages.success(request, f'La cuenta de @{usuario.username} ha sido {estado}.')
        return redirect('core:admin_usuario_lista')
