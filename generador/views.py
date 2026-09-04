from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import TemplateView

from certificados.models import Categoria
from perfil.models import Perfil
from perfil.repositories import get_perfil

from .generator import CVGenerator


class SeleccionarCategoriaView(LoginRequiredMixin, TemplateView):
    """
    Módulo 4: Permite al usuario seleccionar las categorías profesionales
    para adaptar su CV al área deseada.
    """
    template_name = 'generador/seleccionar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(
            usuario=self.request.user,
            is_active=True
        )
        context['perfil'] = get_perfil(self.request.user)
        return context


class GenerarCvView(LoginRequiredMixin, View):
    """
    Genera la versión adaptada del CV según las categorías elegidas.

    Delega la construcción del contexto y el renderizado en ``CVGenerator``.
    Permite incluir u omitir los anexos/certificados completos.
    """
    template_name = 'generador/cv_preview.html'

    def get(self, request, *args, **kwargs):
        perfil = get_object_or_404(Perfil, usuario=request.user)

        # Categorías seleccionadas por el usuario (vía query string)
        cat_ids = request.GET.getlist('categorias')
        categorias_sel = Categoria.objects.filter(
            usuario=request.user,
            id__in=cat_ids,
            is_active=True
        ) if cat_ids else Categoria.objects.none()

        # Flag para incluir (o no) los anexos/certificados en el CV
        incluir_anexos_param = request.GET.get('incluir_anexos', '1')
        incluir_anexos = incluir_anexos_param not in ['0', 'false', 'False']

        # Generar el CV usando la clase extraída
        generator = CVGenerator(
            perfil=perfil,
            categorias_seleccionadas=list(categorias_sel),
            template_name=self.template_name,
        )
        html = generator.generate_html(
            request=request,
            incluir_anexos=incluir_anexos,
        )
        return HttpResponse(html)


class PreviewCvView(LoginRequiredMixin, View):
    """
    Vista previa del CV completo estándar (Módulo 1).

    Usa ``CVGenerator`` sin categorías seleccionadas, de modo que no se
    aplica filtrado y quedan incluidas todas las categorías por defecto
    (CV completo estándar).
    """
    template_name = 'generador/cv_preview.html'

    def get(self, request, *args, **kwargs):
        perfil = get_object_or_404(Perfil, usuario=request.user)

        # Flag para incluir (o no) los anexos/certificados en el CV
        incluir_anexos_param = request.GET.get('incluir_anexos', '1')
        incluir_anexos = incluir_anexos_param not in ['0', 'false', 'False']

        # Todas las categorías por defecto: al no pasar ninguna categoría,
        # CVGenerator no filtra y genera el CV completo estándar.
        generator = CVGenerator(
            perfil=perfil,
            categorias_seleccionadas=[],
            template_name=self.template_name,
        )
        html = generator.generate_html(
            request=request,
            incluir_anexos=incluir_anexos,
        )
        return HttpResponse(html)

