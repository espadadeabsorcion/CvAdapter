from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categorias',
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categoria'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'nombre'],
                name='unique_categoria_usuario',
            )
        ]

    def __str__(self):
        return self.nombre


class Certificado(models.Model):
    perfil = models.ForeignKey(
        'perfil.Perfil',
        on_delete=models.CASCADE,
        related_name='certificados',
    )
    nombre = models.CharField(max_length=255)
    # Nombre original del archivo (sanitizado) — se muestra al usuario
    archivo_url = models.CharField(max_length=255, blank=True)
    # Nombre interno generado por el sistema (UUID.pdf) — fuera de la raíz web
    archivo_interno = models.CharField(max_length=255)
    fecha_obtencion = models.DateField(null=True, blank=True)
    institucion = models.CharField(max_length=200, blank=True)
    categorias = models.ManyToManyField(
        Categoria,
        blank=True,
        related_name='certificados',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'certificado'
        ordering = ['-fecha_obtencion']
        indexes = [
            models.Index(fields=['perfil'], name='idx_certificado_perfil')
        ]

    def __str__(self):
        return self.nombre

