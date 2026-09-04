from django.contrib import admin

from .models import Categoria, Certificado


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'created_at')
    list_filter = ('usuario',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil', 'institucion', 'fecha_obtencion', 'created_at')
    list_filter = ('categorias',)
    search_fields = ('nombre', 'institucion')
    filter_horizontal = ('categorias',)
    ordering = ('-created_at',)
