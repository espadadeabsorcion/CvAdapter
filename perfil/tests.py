from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from .forms import IdiomaForm
from .models import Idioma, Perfil


def _imagen_png(nombre='foto.png'):
    """Genera una pequeña imagen PNG en memoria para los tests."""
    buf = BytesIO()
    Image.new('RGB', (2, 2), color=(200, 30, 30)).save(buf, format='PNG')
    return SimpleUploadedFile(nombre, buf.getvalue(), content_type='image/png')


class IdiomaNivelesCEFRTest(TestCase):
    """
    Validates: Req. 6.5 (niveles de dominio del idioma).

    Los niveles de dominio del idioma se segmentan en la escala CEFR de
    seis tramos: A1, A2, B1, B2, C1 y C2.
    """

    def test_niveles_choices_exactos_cefr(self):
        """El modelo Idioma expone exactamente los 6 niveles CEFR (A1-C2)."""
        valores = [v for v, _ in Idioma.NIVEL_CHOICES]
        self.assertEqual(valores, ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'])

    def test_form_acepta_cada_nivel_cefr(self):
        """Cada nivel CEFR es válido y persistible a través del form."""
        for nivel in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            form = IdiomaForm(data={'idioma': 'Inglés', 'nivel': nivel})
            self.assertTrue(form.is_valid(), f"El nivel {nivel} debería ser válido")
            self.assertEqual(form.cleaned_data['nivel'], nivel)

    def test_form_rechaza_nivel_fuera_de_escala(self):
        """Un nivel no contemplado (p.ej. 'Experto') es rechazado por el form."""
        form = IdiomaForm(data={'idioma': 'Inglés', 'nivel': 'Experto'})
        self.assertFalse(form.is_valid())
        self.assertIn('nivel', form.errors)


class PerfilFotoTest(TestCase):
    """Valida la resolución de la fotografía del perfil (foto_efectiva).

    Prioridad: archivo subido (foto) > enlace externo (foto_url) > vacío.
    """

    def tearDown(self):
        """Elimina los archivos que estos tests suben a MEDIA_ROOT.

        Django no limpia MEDIA_ROOT tras los tests; sin esta limpieza, el
        storage renombrearía fotos futuras con sufijos aleatorios (foto_xxx.png).
        """
        import os

        from django.conf import settings

        carpeta = os.path.join(settings.MEDIA_ROOT, 'perfiles')
        if os.path.isdir(carpeta):
            for nombre in os.listdir(carpeta):
                if nombre.startswith('foto'):
                    try:
                        os.remove(os.path.join(carpeta, nombre))
                    except OSError:
                        pass

    def _crear_perfil(self, **kwargs):
        user = User.objects.create_user(username='fotouser', password='x')
        return Perfil.objects.create(
            usuario=user,
            nombre_completo='Foto Usuario',
            email='foto@test.com',
            telefono='123',
            titulo_profesional='Ing.',
            resumen_profesional='Resumen',
            **kwargs,
        )

    def test_sin_foto_retorna_vacio(self):
        perfil = self._crear_perfil()
        self.assertEqual(perfil.foto_efectiva, '')

    def test_url_como_respaldo(self):
        perfil = self._crear_perfil(foto_url='https://ejemplo.com/foto.jpg')
        self.assertEqual(perfil.foto_efectiva, 'https://ejemplo.com/foto.jpg')

    def test_archivo_tiene_prioridad_sobre_url(self):
        perfil = self._crear_perfil(
            foto=_imagen_png(),
            foto_url='https://ejemplo.com/foto.jpg',
        )
        # El archivo subido tiene prioridad y se sirve desde MEDIA_URL.
        # Nota: no se asume el nombre exacto porque el storage de Django puede
        # renombrar el archivo si ya existe otro con el mismo nombre en disco.
        self.assertTrue(
            perfil.foto_efectiva.startswith('/media/perfiles/'),
            f'URL inesperada para la foto: {perfil.foto_efectiva}',
        )
        self.assertTrue(perfil.foto_efectiva.endswith('.png'))
        self.assertNotEqual(perfil.foto_efectiva, 'https://ejemplo.com/foto.jpg')

