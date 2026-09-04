"""
Capa de Repositorio del módulo ``perfil``.

Sigue el patrón **Model-Repository-Screen**: las vistas (screens) no acceden
directamente a los modelos; delegan el acceso a datos (consultas y lógica de
persistencia) en esta capa de repositorios. Así los modelos permanecen
enfocados en la definición de datos y las pantallas en la presentación.

Todo conjunto de datos con fechas queda ordenado de lo más reciente a lo más
antiguo (requisito general del proyecto).
"""
from .models import Educacion, Experiencia, Habilidad, Idioma, Perfil


# =============================================================================
# Perfil
# =============================================================================

def get_or_create_perfil(usuario) -> tuple:
    """Obtiene el perfil del usuario o lo crea con valores por defecto."""
    return Perfil.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nombre_completo': usuario.get_full_name() or usuario.username,
            'email': usuario.email or f'{usuario.username}@example.com',
            'titulo_profesional': 'Profesional',
            'resumen_profesional': 'Resumen profesional...',
        },
    )


def get_perfil(usuario) -> Perfil:
    """Devuelve el perfil de un usuario (o None si no existe)."""
    return Perfil.objects.filter(usuario=usuario).first()


# =============================================================================
# Experiencia
# =============================================================================

def get_experiencias(perfil, solo_activas=True):
    """Experiencias del perfil, ordenadas de la más reciente a la más antigua."""
    qs = Experiencia.objects.filter(perfil=perfil)
    if solo_activas:
        qs = qs.filter(is_active=True)
    return qs.order_by('-fecha_inicio')


# =============================================================================
# Educación
# =============================================================================

def get_educaciones(perfil, solo_activas=True):
    """Formaciones del perfil, ordenadas de la más reciente a la más antigua."""
    qs = Educacion.objects.filter(perfil=perfil)
    if solo_activas:
        qs = qs.filter(is_active=True)
    return qs.order_by('-fecha_inicio')


# =============================================================================
# Habilidades
# =============================================================================

def get_habilidades(perfil, solo_activas=True, categorias=None):
    """Habilidades del perfil (opcionalmente filtradas por categorías)."""
    qs = Habilidad.objects.filter(perfil=perfil)
    if solo_activas:
        qs = qs.filter(is_active=True)
    if categorias:
        qs = qs.filter(categorias__in=categorias).distinct()
    return qs.order_by('tipo', 'nombre')


def get_habilidades_por_tipo(perfil, tipo, solo_activas=True, categorias=None):
    """Habilidades del perfil agrupadas por tipo (hard | power)."""
    return get_habilidades(perfil, solo_activas, categorias).filter(tipo=tipo)


# =============================================================================
# Idiomas
# =============================================================================

def get_idiomas(perfil, solo_activas=True):
    """Idiomas registrados en el perfil."""
    qs = Idioma.objects.filter(perfil=perfil)
    if solo_activas:
        qs = qs.filter(is_active=True)
    return qs


# =============================================================================
# Certificados (acceso transversal)
# =============================================================================

def get_certificados(perfil, solo_activas=True, categorias=None):
    """Certificados del perfil ordenados por fecha de obtención (recientes primero)."""
    from certificados.models import Certificado

    qs = Certificado.objects.filter(perfil=perfil)
    if solo_activas:
        qs = qs.filter(is_active=True)
    if categorias:
        qs = qs.filter(categorias__in=categorias).distinct()
    return qs.order_by('-fecha_obtencion')

