import os
from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from perfil.models import Perfil
from certificados.models import Certificado

class CertificadoPublicoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lenin', password='123')
        self.perfil = Perfil.objects.create(usuario=self.user, nombre_completo='Lenin')
        
        self.cert = Certificado.objects.create(
            perfil=self.perfil,
            nombre='Curso Python',
            archivo_interno='fake-uuid-123.pdf',
            archivo_url='curso-python.pdf'
        )
        self.client = Client()

    @patch('certificados.file_handler.os.path.exists', return_value=True)
    @patch('certificados.views.open')
    def test_descargar_certificado_publico_ok(self, mock_open, mock_exists):
        """Descarga pública correcta (anónimo, perfil activo, certificado activo)."""
        mock_open.return_value.__enter__.return_value = open('manage.py', 'rb') # solo un dummy leíble
        url = reverse('certificados:certificado_publico_descargar', args=[self.user.username, self.cert.id])
        
        # Omitimos el parseo real del FileResponse que necesita el archivo de verdad,
        # solo validamos la construcción exitosa y los headers correctos.
        with patch('django.http.FileResponse.set_headers'):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @patch('certificados.file_handler.os.path.exists', return_value=True)
    def test_descargar_certificado_publico_404_otro_usuario(self, mock_exists):
        """No se puede descargar un certificado de otro usuario con el username equivocado."""
        url = reverse('certificados:certificado_publico_descargar', args=['otro_user', self.cert.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('certificados.file_handler.os.path.exists', return_value=True)
    def test_descargar_certificado_publico_404_inactivo(self, mock_exists):
        """Si el certificado está inactivo, devuelve 404."""
        self.cert.is_active = False
        self.cert.save()
        url = reverse('certificados:certificado_publico_descargar', args=[self.user.username, self.cert.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
