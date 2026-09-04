from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

from certificados.models import Categoria
from .forms import EducacionForm, ExperienciaForm, HabilidadForm, IdiomaForm, PerfilForm
from .models import Educacion, Experiencia, Habilidad, Idioma, Perfil
from .repositories import get_or_create_perfil


# =============================================================================
# Perfil Base
# =============================================================================

class PerfilView(LoginRequiredMixin, View):
    """Ver y editar los datos base del Perfil Profesional."""
    template_name = 'perfil/perfil_form.html'

    def get(self, request, *args, **kwargs):
        perfil, _ = get_or_create_perfil(request.user)
        form = PerfilForm(instance=perfil)
        return render(request, self.template_name, {'form': form, 'perfil': perfil})

    def post(self, request, *args, **kwargs):
        perfil, _ = get_or_create_perfil(request.user)
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil:perfil_detalle')
        return render(request, self.template_name, {'form': form, 'perfil': perfil})


# =============================================================================
# Experiencia Laboral
# =============================================================================

class ExperienciaListView(LoginRequiredMixin, ListView):
    """Lista de empleos y experiencias laborales."""
    model = Experiencia
    template_name = 'perfil/experiencia_list.html'
    context_object_name = 'experiencias'

    def get_queryset(self):
        return Experiencia.objects.filter(perfil__usuario=self.request.user)


class ExperienciaCreateView(LoginRequiredMixin, CreateView):
    """Crear un registro de experiencia laboral."""
    model = Experiencia
    form_class = ExperienciaForm
    template_name = 'perfil/experiencia_form.html'
    success_url = reverse_lazy('perfil:experiencia_lista')

    def form_valid(self, form):
        perfil, _ = get_or_create_perfil(self.request.user)
        form.instance.perfil = perfil
        messages.success(self.request, 'Experiencia laboral guardada correctamente.')
        return super().form_valid(form)


class ExperienciaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar experiencia laboral."""
    model = Experiencia
    form_class = ExperienciaForm
    template_name = 'perfil/experiencia_form.html'
    success_url = reverse_lazy('perfil:experiencia_lista')

    def get_queryset(self):
        return Experiencia.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Experiencia laboral actualizada.')
        return super().form_valid(form)


class ExperienciaDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar experiencia laboral."""
    model = Experiencia
    template_name = 'perfil/experiencia_confirm_delete.html'
    success_url = reverse_lazy('perfil:experiencia_lista')

    def get_queryset(self):
        return Experiencia.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Experiencia eliminada.')
        return super().form_valid(form)


# =============================================================================
# Educación
# =============================================================================

class EducacionListView(LoginRequiredMixin, ListView):
    """Lista de registros de educación."""
    model = Educacion
    template_name = 'perfil/educacion_list.html'
    context_object_name = 'educaciones'

    def get_queryset(self):
        return Educacion.objects.filter(perfil__usuario=self.request.user)


class EducacionCreateView(LoginRequiredMixin, CreateView):
    """Crear un registro de educación."""
    model = Educacion
    form_class = EducacionForm
    template_name = 'perfil/educacion_form.html'
    success_url = reverse_lazy('perfil:educacion_lista')

    def form_valid(self, form):
        perfil, _ = get_or_create_perfil(self.request.user)
        form.instance.perfil = perfil
        messages.success(self.request, 'Educación guardada correctamente.')
        return super().form_valid(form)


class EducacionUpdateView(LoginRequiredMixin, UpdateView):
    """Editar educación."""
    model = Educacion
    form_class = EducacionForm
    template_name = 'perfil/educacion_form.html'
    success_url = reverse_lazy('perfil:educacion_lista')

    def get_queryset(self):
        return Educacion.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Educación actualizada correctamente.')
        return super().form_valid(form)


class EducacionDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar educación."""
    model = Educacion
    template_name = 'perfil/educacion_confirm_delete.html'
    success_url = reverse_lazy('perfil:educacion_lista')

    def get_queryset(self):
        return Educacion.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Educación eliminada.')
        return super().form_valid(form)


# =============================================================================
# Habilidades
# =============================================================================

class HabilidadListView(LoginRequiredMixin, ListView):
    """Lista de habilidades."""
    model = Habilidad
    template_name = 'perfil/habilidad_list.html'
    context_object_name = 'habilidades'

    def get_queryset(self):
        return Habilidad.objects.filter(
            perfil__usuario=self.request.user
        ).prefetch_related('categorias')


class HabilidadCreateView(LoginRequiredMixin, CreateView):
    """Crear una habilidad."""
    model = Habilidad
    form_class = HabilidadForm
    template_name = 'perfil/habilidad_form.html'
    success_url = reverse_lazy('perfil:habilidad_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        perfil, _ = get_or_create_perfil(self.request.user)
        kwargs['perfil'] = perfil
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['categorias'].queryset = Categoria.objects.filter(
            usuario=self.request.user
        )
        return form

    def form_valid(self, form):
        perfil, _ = get_or_create_perfil(self.request.user)
        form.instance.perfil = perfil
        messages.success(self.request, 'Habilidad guardada correctamente.')
        return super().form_valid(form)


class HabilidadUpdateView(LoginRequiredMixin, UpdateView):
    """Editar una habilidad."""
    model = Habilidad
    form_class = HabilidadForm
    template_name = 'perfil/habilidad_form.html'
    success_url = reverse_lazy('perfil:habilidad_lista')

    def get_queryset(self):
        return Habilidad.objects.filter(perfil__usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        perfil, _ = get_or_create_perfil(self.request.user)
        kwargs['perfil'] = perfil
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['categorias'].queryset = Categoria.objects.filter(
            usuario=self.request.user
        )
        return form

    def form_valid(self, form):
        messages.success(self.request, 'Habilidad actualizada correctamente.')
        return super().form_valid(form)


class HabilidadDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar una habilidad."""
    model = Habilidad
    template_name = 'perfil/habilidad_confirm_delete.html'
    success_url = reverse_lazy('perfil:habilidad_lista')

    def get_queryset(self):
        return Habilidad.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Habilidad eliminada.')
        return super().form_valid(form)


# =============================================================================
# Idiomas
# =============================================================================

class IdiomaListView(LoginRequiredMixin, ListView):
    """Lista de idiomas."""
    model = Idioma
    template_name = 'perfil/idioma_list.html'
    context_object_name = 'idiomas'

    def get_queryset(self):
        return Idioma.objects.filter(perfil__usuario=self.request.user)


class IdiomaCreateView(LoginRequiredMixin, CreateView):
    """Registrar un nuevo idioma."""
    model = Idioma
    form_class = IdiomaForm
    template_name = 'perfil/idioma_form.html'
    success_url = reverse_lazy('perfil:idioma_lista')

    def form_valid(self, form):
        perfil, _ = get_or_create_perfil(self.request.user)
        form.instance.perfil = perfil
        messages.success(self.request, 'Idioma guardado correctamente.')
        return super().form_valid(form)


class IdiomaUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un idioma."""
    model = Idioma
    form_class = IdiomaForm
    template_name = 'perfil/idioma_form.html'
    success_url = reverse_lazy('perfil:idioma_lista')

    def get_queryset(self):
        return Idioma.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Idioma actualizado.')
        return super().form_valid(form)


class IdiomaDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar un idioma."""
    model = Idioma
    template_name = 'perfil/idioma_confirm_delete.html'
    success_url = reverse_lazy('perfil:idioma_lista')

    def get_queryset(self):
        return Idioma.objects.filter(perfil__usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Idioma eliminado.')
        return super().form_valid(form)
