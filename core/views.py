from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.views import View


class CustomLoginView(LoginView):
    """
    LoginView personalizada que muestra un mensaje genérico en caso de
    credenciales inválidas, sin revelar si fue el usuario o la contraseña
    lo que falló (Req. 1.2).
    """
    template_name = 'core/login.html'

    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir al dashboard (Req. 1.1)
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        # Limpiar errores de campo y mostrar solo mensaje genérico (Req. 1.2)
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
    Vista raíz (/). Redirige al dashboard si hay sesión activa,
    al login si no la hay (Req. 1.5).
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return redirect('core:login')
