from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .file_handler import CertificadoFileHandler
from .models import Categoria, Certificado


class CategoriaForm(forms.ModelForm):
    """
    Formulario para crear y editar Categorías.
    Sanitiza los campos de texto con strip_tags y valida unicidad por usuario.
    """

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise forms.ValidationError('El nombre de la categoría es obligatorio.')
        nombre = strip_tags(nombre)
        if self.usuario:
            qs = Categoria.objects.filter(
                usuario=self.usuario,
                nombre__iexact=nombre,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'Ya existe una categoría con ese nombre.'
                )
        return nombre

    def clean_descripcion(self):
        desc = self.cleaned_data.get('descripcion', '')
        return strip_tags(desc) if desc else ''


class CertificadoForm(forms.ModelForm):
    """
    Formulario para la subida y gestión de Certificados en PDF.
    Criterios de seguridad:
    - Validación de extensión (.pdf) y tipo MIME (application/pdf).
    - Límite de tamaño máximo: 5 MB (5 * 1024 * 1024 bytes).
    - Guardado seguro en disco con nombre interno único UUID.pdf.
    """

    archivo_pdf = forms.FileField(
        label='Archivo PDF',
        required=False,
        help_text='Solo archivos PDF, máximo 5MB.',
    )

    class Meta:
        model = Certificado
        fields = ['nombre', 'institucion', 'fecha_obtencion', 'categorias']
        widgets = {
            'fecha_obtencion': forms.DateInput(attrs={'type': 'date'}),
            'categorias': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        # Si es edición, el archivo no es estrictamente obligatorio
        if not self.instance.pk:
            self.fields['archivo_pdf'].required = True

        if usuario:
            self.fields['categorias'].queryset = Categoria.objects.filter(
                usuario=usuario
            )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        return strip_tags(nombre) if nombre else ''

    def clean_institucion(self):
        inst = self.cleaned_data.get('institucion', '').strip()
        return strip_tags(inst) if inst else ''

    def clean_archivo_pdf(self):
        archivo = self.cleaned_data.get('archivo_pdf')
        if not archivo:
            if not self.instance.pk:
                raise ValidationError('Debe seleccionar un archivo PDF.')
            return None

        # Las excepciones del handler son subclases de ValidationError,
        # por lo que se propagan directamente y Django las muestra correctamente.
        CertificadoFileHandler.validate_file(archivo)

        return archivo

    def save(self, commit=True):
        instance = super().save(commit=False)
        archivo = self.cleaned_data.get('archivo_pdf')

        if archivo:
            CertificadoFileHandler.save_file(archivo, instance)
            instance.archivo_url = strip_tags(archivo.name)

        if commit:
            instance.save()
            self.save_m2m()
        return instance
