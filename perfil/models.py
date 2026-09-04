from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Perfil(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='perfil'
    )
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    telefono = models.CharField(max_length=20)
    titulo_profesional = models.CharField(max_length=100)
    resumen_profesional = models.TextField(max_length=1000)
    foto_url = models.URLField(blank=True)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    linkedin = models.URLField(blank=True)
    ubicacion = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perfil'
        indexes = [models.Index(fields=['usuario'], name='idx_perfil_usuario')]

    def __str__(self):
        return self.nombre_completo

    @property
    def foto_efectiva(self):
        """Retorna la URL de la fotografía a mostrar en el CV.

        Prioriza el archivo de imagen subido (foto); si no existe, usa el
        enlace externo (foto_url) como respaldo.
        """
        if self.foto:
            return self.foto.url
        return self.foto_url or ''


class Experiencia(models.Model):
    perfil = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, related_name='experiencias'
    )
    empresa = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    actual = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'experiencia'
        indexes = [models.Index(fields=['perfil'], name='idx_experiencia_perfil')]
        ordering = ['-fecha_inicio']

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError(
                {'fecha_fin': 'La fecha de fin no puede ser anterior a la de inicio.'}
            )

    def __str__(self):
        return f"{self.cargo} en {self.empresa}"


class Educacion(models.Model):
    perfil = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, related_name='educaciones'
    )
    institucion = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'educacion'
        ordering = ['-fecha_inicio']

    def clean(self):
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            raise ValidationError(
                {'fecha_fin': 'La fecha de fin no puede ser anterior a la de inicio.'}
            )

    def __str__(self):
        return f"{self.titulo} — {self.institucion}"


class Habilidad(models.Model):
    """Habilidad o competencia del perfil.

    Se clasifica en dos grandes grupos (Req: separar en 'Hard Skills' y
    'Power Skills'), lo que permite agruparlas en el CV en filas/columnas.
    """

    TIPO_CHOICES = [
        ('hard', 'Hard Skills'),
        ('power', 'Power Skills'),
    ]

    perfil = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, related_name='habilidades'
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=20, choices=TIPO_CHOICES, default='hard'
    )
    nivel = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3
    )
    categorias = models.ManyToManyField(
        'certificados.Categoria', blank=True, related_name='habilidades'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'habilidad'
        constraints = [
            models.UniqueConstraint(
                fields=['perfil', 'nombre'],
                name='unique_habilidad_perfil'
            )
        ]

    def __str__(self):
        return self.nombre


class Idioma(models.Model):
    NIVEL_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    perfil = models.ForeignKey(
        Perfil, on_delete=models.CASCADE, related_name='idiomas'
    )
    idioma = models.CharField(max_length=100)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'idioma'

    def __str__(self):
        return f"{self.idioma} ({self.nivel})"

