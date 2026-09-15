import os
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from perfil.models import Perfil
from .file_handler import CertificadoFileHandler
from .forms import CategoriaForm, CertificadoForm
from .models import Categoria, Certificado


# =============================================================================
# Vistas de Categorías (Req. 3.1–3.4)
# =============================================================================

class CategoriaListView(LoginRequiredMixin, ListView):
    """Lista las categorías creadas por el usuario autenticado."""
    model = Categoria
    template_name = 'certificados/categoria_list.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user, is_active=True)


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    """Crear nueva categoría."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'certificados/categoria_form.html'
    success_url = reverse_lazy('certificados:categoria_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Categoría creada con éxito.')
        return super().form_valid(form)


class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar categoría existente."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'certificados/categoria_form.html'
    success_url = reverse_lazy('certificados:categoria_lista')

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Categoría actualizada con éxito.')
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar categoría."""
    model = Categoria
    template_name = 'certificados/categoria_confirm_delete.html'
    success_url = reverse_lazy('certificados:categoria_lista')

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Categoría eliminada.')
        return super().form_valid(form)


# =============================================================================
# Vistas de Certificados (Req. 2.1–2.4)
# =============================================================================

class CertificadoListView(LoginRequiredMixin, ListView):
    """Lista los certificados asociados al perfil del usuario autenticado."""
    model = Certificado
    template_name = 'certificados/certificado_list.html'
    context_object_name = 'certificados'

    def get_queryset(self):
        return Certificado.objects.filter(
            perfil__usuario=self.request.user,
            is_active=True
        ).prefetch_related('categorias')


class CertificadoCreateView(LoginRequiredMixin, CreateView):
    """Subir un nuevo certificado en PDF."""
    model = Certificado
    form_class = CertificadoForm
    template_name = 'certificados/certificado_form.html'
    success_url = reverse_lazy('certificados:certificado_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        perfil, _ = Perfil.objects.get_or_create(
            usuario=self.request.user,
            defaults={
                'nombre_completo': self.request.user.get_full_name() or self.request.user.username,
                'email': self.request.user.email or f"{self.request.user.username}@example.com",
                'titulo_profesional': 'Profesional',
                'resumen_profesional': 'Perfil en construcción.',
            }
        )
        form.instance.perfil = perfil
        messages.success(self.request, 'Certificado PDF subido correctamente.')
        return super().form_valid(form)


class CertificadoUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un certificado existente (nombre, institución, fecha, categorías o reemplazar PDF)."""
    model = Certificado
    form_class = CertificadoForm
    template_name = 'certificados/certificado_form.html'
    success_url = reverse_lazy('certificados:certificado_lista')

    def get_queryset(self):
        return Certificado.objects.filter(perfil__usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['usuario'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Certificado actualizado correctamente.')
        return super().form_valid(form)



class CertificadoDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar certificado y su archivo físico del servidor."""
    model = Certificado
    template_name = 'certificados/certificado_confirm_delete.html'
    success_url = reverse_lazy('certificados:certificado_lista')

    def get_queryset(self):
        return Certificado.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        certificado = self.get_object()
        # Eliminar archivo físico si existe (gestionado por el handler)
        CertificadoFileHandler.delete_file(certificado)
        messages.success(self.request, 'Certificado eliminado.')
        return super().form_valid(form)


class CertificadoDownloadView(LoginRequiredMixin, View):
    """Servicio seguro de descarga o visualización de PDF subido."""
    def get(self, request, pk, *args, **kwargs):
        certificado = get_object_or_404(
            Certificado,
            pk=pk,
            perfil__usuario=request.user
        )
        path_archivo = CertificadoFileHandler.get_file_path(certificado)
        if not path_archivo or not os.path.exists(path_archivo):
            raise Http404("El archivo PDF no fue encontrado en el servidor.")

        return FileResponse(
            open(path_archivo, 'rb'),
            content_type='application/pdf',
            filename=certificado.archivo_url or f"certificado_{certificado.pk}.pdf"
        )


class CertificadoPublicoDownloadView(View):
    """
    Servicio público (sin login) de descarga/visualización de un certificado.

    Multi-usuario: el perfil dueño se identifica por ``username`` en la URL.
    Solo son accesibles los certificados activos de perfiles activos de
    usuarios activos; cualquier otro intento devuelve 404 (así un perfil
    desactivado retira de inmediato sus certificados del dominio público).
    """
    def get(self, request, username, pk, *args, **kwargs):
        certificado = get_object_or_404(
            Certificado,
            pk=pk,
            is_active=True,
            perfil__is_active=True,
            perfil__usuario__username=username,
            perfil__usuario__is_active=True,
        )
        path_archivo = CertificadoFileHandler.get_file_path(certificado)
        if not path_archivo or not os.path.exists(path_archivo):
            raise Http404("El archivo PDF no fue encontrado en el servidor.")

        return FileResponse(
            open(path_archivo, 'rb'),
            content_type='application/pdf',
            filename=certificado.archivo_url or f"certificado_{certificado.pk}.pdf"
        )
