"""
Capa de Generación del módulo ``generador``.

Contiene la clase ``CVGenerator``, responsable de construir el contexto de
datos con el que se renderiza el CV y de producir su representación HTML
(Listo para ser ampliado a PDF en el futuro).

Sigue el mismo patrón del proyecto: la lógica de consulta a datos se delega
en la capa de repositorios (``perfil.repositories``), de modo que aquí no se
accede directamente a los modelos excepto para identificar las categorías.
"""
from django.template.loader import render_to_string

from perfil.repositories import (
    get_certificados,
    get_educaciones,
    get_experiencias,
    get_habilidades_por_tipo,
    get_idiomas,
)


class CVGenerator:
    """
    Genera el contexto y el HTML de un CV a partir del perfil del usuario y
    de una lista de categorías seleccionadas.

    Si se proporcionan categorías, filtra las Habilidades y los Certificados
    a aquellas asignadas a dichas categorías. Experiencias, Educación e
    Idiomas siempre se incluyen completos (no se filtran).

    Atributos:
        perfil (Perfil): Perfil profesional del usuario.
        categorias (list): Categorías seleccionadas (objetos o IDs).
        template_name (str): Template del CV a renderizar.
    """

    def __init__(self, perfil, categorias_seleccionadas=None, template_name='generador/cv_preview.html'):
        self.perfil = perfil
        self.categorias_seleccionadas = categorias_seleccionadas or []
        self.template_name = template_name

    # ------------------------------------------------------------------ #
    # Utilidades
    # ------------------------------------------------------------------ #
    def _filtrar_categorias(self, incluir_anexos=False):
        """
        Prepara la lista de IDs de categorías para el filtrado de consultas.

        Retorna:
            - Una lista de IDs de categorías si el usuario seleccionó alguna.
            - ``None`` si no hay ninguna categoría seleccionada (sin filtrado).
        """
        if not self.categorias_seleccionadas:
            return None

        # Aceptar tanto objetos Categoria como IDs enteros
        ids = [
            c.id if hasattr(c, 'id') else int(c)
            for c in self.categorias_seleccionadas
        ]
        return ids if ids else None

    # ------------------------------------------------------------------ #
    # Contexto de datos
    # ------------------------------------------------------------------ #
    def get_context_data(self, incluir_anexos=True):
        """
        Construye el diccionario de contexto con los datos del CV.

        Filtra Habilidades y Certificados por las categorías seleccionadas.
        Experiencias, Educación e Idiomas se incluyen siempre completos.

        Argumentos:
            incluir_anexos (bool): Si es ``True`` (por defecto) el contexto
                incluye los certificados en la sección de anexos; si es
                ``False`` se omiten (dejando la sección vacía).

        Retorna:
            dict: Contexto listo para ser usado por el template del CV.
        """
        categorias_ids = self._filtrar_categorias()
        filtrado = categorias_ids is not None

        # Datos filtrados por categorías (habilidades y certificados)
        habilidades_hard = get_habilidades_por_tipo(
            self.perfil, 'hard', categorias=categorias_ids
        )
        habilidades_power = get_habilidades_por_tipo(
            self.perfil, 'power', categorias=categorias_ids
        )
        certificados = get_certificados(
            self.perfil, categorias=categorias_ids
        )

        # Datos no filtrados (siempre completos)
        experiencias = get_experiencias(self.perfil)
        educaciones = get_educaciones(self.perfil)
        idiomas = get_idiomas(self.perfil)

        return {
            'perfil': self.perfil,
            'experiencias': experiencias,
            'educaciones': educaciones,
            'habilidades_hard': habilidades_hard,
            'habilidades_power': habilidades_power,
            'idiomas': idiomas,
            'certificados': certificados if incluir_anexos else certificados.none(),
            'todos_certificados': certificados,
            'categorias_seleccionadas': self.categorias_seleccionadas,            'filtrado': filtrado,
            'incluir_anexos': incluir_anexos,
        }

    # ------------------------------------------------------------------ #
    # Renderizado
    # ------------------------------------------------------------------ #
    def generate_html(self, request=None, incluir_anexos=True):
        """
        Renderiza el template del CV con el contexto construido.

        Argumentos:
            request (HttpRequest, opcional): Request actual, necesario si el
                template usa ``{% url %}`` con ``request`` en el contexto.
            incluir_anexos (bool): Indica si se incluyen los certificados
                como anexos en el CV renderizado.

        Retorna:
            str: HTML renderizado del CV.
        """
        context = self.get_context_data(incluir_anexos=incluir_anexos)
        return render_to_string(self.template_name, context, request=request)

    # ------------------------------------------------------------------ #
    # Exportación PDF (preparado para el futuro)
    # ------------------------------------------------------------------ #
    def generate_pdf(self, request=None, incluir_anexos=True):
        """
        Produce el documento final del CV.

        Por ahora la generación PDF se prepara para el futuro; el método
        devuelve el HTML renderizado. Cuando se integre una librería PDF
        (p. ej. WeasyPrint, xhtml2pdf o wkhtmltopdf), aquí se transformará
        el HTML a un objeto/bytes PDF.

        Retorna:
            str: HTML renderizado del CV.
        """
        # TODO: integrar WeasyPrint para generación real de PDF
        return self.generate_html(request=request, incluir_anexos=incluir_anexos)
