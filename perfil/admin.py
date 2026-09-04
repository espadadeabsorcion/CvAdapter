from django.contrib import admin

from .models import Educacion, Experiencia, Habilidad, Idioma, Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'email', 'titulo_profesional', 'ubicacion', 'linkedin', 'updated_at')
    search_fields = ('nombre_completo', 'email')


@admin.register(Experiencia)
class ExperienciaAdmin(admin.ModelAdmin):
    list_display = ('cargo', 'empresa', 'fecha_inicio', 'fecha_fin', 'actual')
    list_filter = ('actual',)
    ordering = ('-fecha_inicio',)


@admin.register(Educacion)
class EducacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'institucion', 'fecha_inicio', 'fecha_fin')
    ordering = ('-fecha_inicio',)


@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'perfil', 'nivel')
    list_filter = ('nivel', 'tipo')
    filter_horizontal = ('categorias',)


@admin.register(Idioma)
class IdiomaAdmin(admin.ModelAdmin):
    list_display = ('idioma', 'nivel', 'perfil')
    list_filter = ('nivel',)
