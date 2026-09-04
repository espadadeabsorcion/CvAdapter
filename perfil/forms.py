from django import forms
from django.utils.html import strip_tags

from .models import Educacion, Experiencia, Habilidad, Idioma, Perfil


class PerfilForm(forms.ModelForm):
    """
    Formulario para crear/editar el Perfil profesional.
    Sanitiza todos los campos de texto con strip_tags (Req. 2.7).
    """

    class Meta:
        model = Perfil
        fields = [
            'nombre_completo',
            'email',
            'telefono',
            'titulo_profesional',
            'resumen_profesional',
            'foto',
            'foto_url',
            'linkedin',
            'ubicacion',
        ]

    def clean(self):
        cleaned_data = super().clean()
        # Sanitizar campos de texto para prevenir inyección de código (Req. 2.7)
        text_fields = [
            'nombre_completo',
            'telefono',
            'titulo_profesional',
            'resumen_profesional',
            'ubicacion',
        ]
        for field in text_fields:
            value = cleaned_data.get(field)
            if value:
                cleaned_data[field] = strip_tags(value)
        return cleaned_data


class ExperienciaForm(forms.ModelForm):
    """
    Formulario para crear/editar registros de Experiencia laboral.
    Valida que fecha_fin no sea anterior a fecha_inicio (Req. 3.5).
    Los campos empresa, cargo y fecha_inicio son obligatorios (Req. 3.2).
    """

    class Meta:
        model = Experiencia
        fields = [
            'empresa',
            'cargo',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
            'actual',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        # Validar rango de fechas (Req. 3.5)
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            self.add_error(
                'fecha_fin',
                'La fecha de fin no puede ser anterior a la de inicio.',
            )
        return cleaned_data


class EducacionForm(forms.ModelForm):
    """
    Formulario para crear/editar registros de Educación.
    Valida obligatoriedad y longitud de institución y título (Req. 4.4, 4.5).
    Valida fecha_inicio obligatoria y formato válido (Req. 4.6).
    Valida que fecha_fin no sea anterior a fecha_inicio (Req. 4.7).
    """

    class Meta:
        model = Educacion
        fields = [
            'institucion',
            'titulo',
            'descripcion',
            'fecha_inicio',
            'fecha_fin',
        ]
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        # Validar rango de fechas (Req. 4.7)
        if fecha_fin and fecha_inicio and fecha_fin < fecha_inicio:
            self.add_error(
                'fecha_fin',
                'La fecha de fin no puede ser anterior a la de inicio.',
            )
        return cleaned_data


class HabilidadForm(forms.ModelForm):
    """
    Formulario para crear/editar Habilidades.
    Valida unicidad del nombre por perfil (case-insensitive) (Req. 5.2, 5.3).
    Muestra error específico si el nombre está duplicado o fuera del rango (Req. 5.4).
    """

    class Meta:
        model = Habilidad
        fields = ['nombre', 'tipo', 'nivel', 'categorias']
        widgets = {
            'categorias': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, perfil=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.perfil = perfil

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre de la habilidad es obligatorio.')
        if self.perfil:
            qs = Habilidad.objects.filter(
                perfil=self.perfil,
                nombre__iexact=nombre,
            )
            # Excluir el registro actual al editar (Req. 5.3)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'Ya existe una habilidad con ese nombre.'
                )
        return nombre


class IdiomaForm(forms.ModelForm):
    """
    Formulario para crear/editar Idiomas.
    Restringe el campo nivel a las opciones CEFR definidas en el modelo (A1-C2).
    Valida que el nombre del idioma no esté vacío y no exceda 100 caracteres (Req. 6.4).
    """

    class Meta:
        model = Idioma
        fields = ['idioma', 'nivel']
