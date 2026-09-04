import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from perfil.models import Perfil
from certificados.models import Categoria, Certificado


class CertificadoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lenin', password='password123')
        self.client = Client(enforce_csrf_checks=False)
        self.client.force_login(self.user)
        self.perfil = Perfil.objects.create(
            usuario=self.user,
            nombre_completo='Lenin Ramírez',
            email='lenin@example.com',
            telefono='+593991234567',
            titulo_profesional='HR Specialist',
            resumen_profesional='Experto en desarrollo organizacional'
        )

    def test_crear_categoria(self):
        """Verifica la creación de categoría por el usuario."""
        response = self.client.post(reverse('certificados:categoria_nueva'), {
            'nombre': 'Desarrollo Web',
            'descripcion': 'Proyectos y habilidades Frontend/Backend'
        })
        self.assertRedirects(response, reverse('certificados:categoria_lista'))
        self.assertTrue(Categoria.objects.filter(usuario=self.user, nombre='Desarrollo Web').exists())

    def test_subida_certificado_pdf_valido(self):
        """Verifica la subida exitosa de un archivo PDF de prueba."""
        cat = Categoria.objects.create(usuario=self.user, nombre='Tech')
        pdf_content = b'%PDF-1.4 test pdf content'
        archivo = SimpleUploadedFile('cert_demo.pdf', pdf_content, content_type='application/pdf')

        response = self.client.post(reverse('certificados:certificado_nuevo'), {
            'nombre': 'Certificado Django Expert',
            'institucion': 'Udemy',
            'archivo_pdf': archivo,
            'categorias': [cat.id]
        })
        self.assertRedirects(response, reverse('certificados:certificado_lista'))
        cert = Certificado.objects.get(nombre='Certificado Django Expert')
        self.assertEqual(cert.archivo_url, 'cert_demo.pdf')
        self.assertTrue(cert.archivo_interno.endswith('.pdf'))

        # Clean up created file
        path_archivo = os.path.join(settings.BASE_DIR, 'media', 'certificados', cert.archivo_interno)
        if os.path.exists(path_archivo):
            os.remove(path_archivo)

    def test_rechazo_archivo_no_pdf(self):
        """Verifica que archivos que no sean PDF sean rechazados con error."""
        cat = Categoria.objects.create(usuario=self.user, nombre='Tech')
        txt_content = b'Hello world text file'
        archivo = SimpleUploadedFile('document.txt', txt_content, content_type='text/plain')

        response = self.client.post(reverse('certificados:certificado_nuevo'), {
            'nombre': 'Certificado Inválido',
            'archivo_pdf': archivo,
            'categorias': [cat.id]
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('archivo_pdf', form.errors)
        self.assertIn('Solo se permiten archivos con extensión .pdf.', form.errors['archivo_pdf'])

    def test_editar_certificado(self):
        """Verifica que un certificado se pueda editar actualizando su nombre e institución sin requerir resubir el PDF."""
        cat = Categoria.objects.create(usuario=self.user, nombre='Tech')
        cert = Certificado.objects.create(
            perfil=self.perfil,
            nombre='Certificado Original',
            institucion='Institucion Original',
            archivo_url='original.pdf',
            archivo_interno='uuid_original.pdf'
        )
        cert.categorias.add(cat)

        response = self.client.post(reverse('certificados:certificado_editar', kwargs={'pk': cert.pk}), {
            'nombre': 'Certificado Editado',
            'institucion': 'Institucion Editada',
            'categorias': [cat.id]
        })
        self.assertRedirects(response, reverse('certificados:certificado_lista'))
        cert.refresh_from_db()
        self.assertEqual(cert.nombre, 'Certificado Editado')
        self.assertEqual(cert.institucion, 'Institucion Editada')
        self.assertEqual(cert.archivo_url, 'original.pdf')


