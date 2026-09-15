"""
core/tests_user_crud.py

Tests para el auto-registro, eliminación de cuenta propia y CRUD de usuarios para Admin.
"""

from unittest.mock import patch
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from perfil.models import Perfil, Habilidad
from certificados.models import Certificado


class RegistroUsuarioTests(TestCase):
    """Pruebas del auto-registro de nuevos usuarios."""

    def setUp(self):
        self.client = Client()

    def test_get_registro_form_ok(self):
        """GET /registro/ retorna formulario de registro con status 200."""
        response = self.client.get(reverse('core:registro'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Crear Cuenta')
        self.assertContains(response, 'Nombre Completo')

    def test_registro_usuario_exitoso(self):
        """POST con datos válidos crea User y Perfil base e inicia sesión."""
        response = self.client.post(reverse('core:registro'), {
            'nombre_completo': 'María González',
            'username': 'mgonzalez',
            'email': 'mgonzalez@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertRedirects(response, reverse('perfil:perfil_detalle'))

        # Verificar en base de datos
        user = User.objects.filter(username='mgonzalez').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'mgonzalez@example.com')
        self.assertTrue(user.check_password('Password123!'))

        # Verificar creación automática del perfil
        self.assertTrue(hasattr(user, 'perfil'))
        self.assertEqual(user.perfil.nombre_completo, 'María González')
        self.assertEqual(user.perfil.email, 'mgonzalez@example.com')

    def test_registro_usuario_duplicado_falla(self):
        """No se puede registrar un username ya existente."""
        User.objects.create_user(username='mgonzalez', password='Password123!')
        response = self.client.post(reverse('core:registro'), {
            'nombre_completo': 'Otra María',
            'username': 'mgonzalez',
            'email': 'otra@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Este nombre de usuario ya está registrado.')

    def test_registro_contrasenas_no_coinciden_falla(self):
        """Si las contraseñas no coinciden, muestra error."""
        response = self.client.post(reverse('core:registro'), {
            'nombre_completo': 'Pedro Gómez',
            'username': 'pgomez',
            'email': 'pgomez@example.com',
            'password': 'Password123!',
            'password_confirm': 'Diferente123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas no coinciden.')

    def test_usuario_autenticado_en_registro_redirige_dashboard(self):
        """Un usuario ya autenticado es redirigido al dashboard si entra a /registro/."""
        user = User.objects.create_user(username='ya_logueado', password='123')
        self.client.force_login(user)
        response = self.client.get(reverse('core:registro'))
        self.assertRedirects(response, reverse('core:dashboard'))


class EliminarCuentaPropiaTests(TestCase):
    """Pruebas de auto-eliminación de cuenta por parte del usuario."""

    def setUp(self):
        self.user = User.objects.create_user(username='usuario_eliminar', password='PasswordSeguro123!')
        self.perfil = Perfil.objects.create(
            usuario=self.user,
            nombre_completo='Usuario Para Borrar',
            email='borrar@example.com'
        )
        self.client = Client()

    def test_eliminar_cuenta_sin_login_redirige(self):
        """GET /eliminar-cuenta/ sin login redirige a /login/."""
        response = self.client.get(reverse('core:eliminar_cuenta'))
        self.assertEqual(response.status_code, 302)

    def test_eliminar_cuenta_password_incorrecto_falla(self):
        """POST con contraseña errónea no borra la cuenta."""
        self.client.force_login(self.user)
        response = self.client.post(reverse('core:eliminar_cuenta'), {
            'password': 'PasswordErroneo!',
            'confirmacion': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La contraseña ingresada es incorrecta.')
        self.assertTrue(User.objects.filter(username='usuario_eliminar').exists())

    def test_eliminar_cuenta_sin_confirmacion_falla(self):
        """POST sin checkbox de confirmación no borra la cuenta."""
        self.client.force_login(self.user)
        response = self.client.post(reverse('core:eliminar_cuenta'), {
            'password': 'PasswordSeguro123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='usuario_eliminar').exists())

    @patch('certificados.file_handler.CertificadoFileHandler.delete_file')
    def test_eliminar_cuenta_exitosa_limpia_recursos(self, mock_delete_file):
        """POST válido elimina el usuario, su perfil, certificados y cierra la sesión."""
        # Usuario de respaldo para que la raíz siga teniendo un perfil publicado
        otro_user = User.objects.create_user(username='otro_usuario', password='123')
        Perfil.objects.create(usuario=otro_user, nombre_completo='Otro Usuario')

        # Asociar un certificado
        cert = Certificado.objects.create(
            perfil=self.perfil,
            nombre='Certificado Test',
            archivo_interno='uuid-borrar.pdf'
        )
        self.client.force_login(self.user)
        response = self.client.post(reverse('core:eliminar_cuenta'), {
            'password': 'PasswordSeguro123!',
            'confirmacion': True,
        })
        self.assertRedirects(response, reverse('root'))

        # Usuario y Perfil eliminados
        self.assertFalse(User.objects.filter(username='usuario_eliminar').exists())
        self.assertFalse(Perfil.objects.filter(pk=self.perfil.pk).exists())
        self.assertFalse(Certificado.objects.filter(pk=cert.pk).exists())
        # Manejador de borrado de archivo invocado
        mock_delete_file.assert_called()


class AdminUsuarioCrudTests(TestCase):
    """Pruebas del CRUD de administración de usuarios (Staff / Admin)."""

    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_boss',
            password='AdminPass123!',
            is_staff=True,
            is_superuser=True
        )
        self.normal_user = User.objects.create_user(
            username='user_normal',
            password='NormalPass123!',
            is_staff=False
        )
        self.perfil_normal = Perfil.objects.create(
            usuario=self.normal_user,
            nombre_completo='Normal User',
            email='normal@example.com'
        )
        self.client = Client()

    def test_acceso_denegado_para_usuario_no_staff(self):
        """Un usuario normal recibe 403 al intentar acceder al listado admin."""
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse('core:admin_usuario_lista'))
        self.assertEqual(response.status_code, 403)

    def test_staff_puede_ver_listado_usuarios(self):
        """Un usuario staff ve el listado de usuarios con status 200."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('core:admin_usuario_lista'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin_boss')
        self.assertContains(response, 'user_normal')

    def test_admin_crea_usuario_exitosamente(self):
        """Admin puede crear un nuevo usuario con perfil y permisos."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('core:admin_usuario_nuevo'), {
            'nombre_completo': 'Nuevo Usuario Admin',
            'username': 'nuevo_staff',
            'email': 'nuevo@example.com',
            'password': 'PasswordSegura123!',
            'is_staff': True,
            'is_active': True,
        })
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))

        created = User.objects.filter(username='nuevo_staff').first()
        self.assertIsNotNone(created)
        self.assertTrue(created.is_staff)
        self.assertEqual(created.perfil.nombre_completo, 'Nuevo Usuario Admin')

    def test_admin_edita_usuario_exitosamente(self):
        """Admin puede modificar datos y permisos de un usuario."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('core:admin_usuario_editar', args=[self.normal_user.pk]), {
            'nombre_completo': 'Normal User Modificado',
            'username': 'user_modificado',
            'email': 'modificado@example.com',
            'is_staff': True,
            'is_active': True,
        })
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))

        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.username, 'user_modificado')
        self.assertEqual(self.normal_user.email, 'modificado@example.com')
        self.assertTrue(self.normal_user.is_staff)
        self.assertEqual(self.normal_user.perfil.nombre_completo, 'Normal User Modificado')

    def test_admin_toggle_active_usuario(self):
        """Admin puede suspender y reactivar usuarios rápidamente."""
        self.client.force_login(self.admin_user)
        url = reverse('core:admin_usuario_toggle_active', args=[self.normal_user.pk])

        # 1. Suspender
        response = self.client.post(url)
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.is_active)

        # 2. Reactivar
        response = self.client.post(url)
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_active)

    def test_admin_no_puede_suspenderse_a_si_mismo(self):
        """Admin no puede suspender su propia cuenta desde el toggle."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('core:admin_usuario_toggle_active', args=[self.admin_user.pk]))
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))
        self.admin_user.refresh_from_db()
        self.assertTrue(self.admin_user.is_active)

    def test_admin_no_puede_eliminarse_a_si_mismo(self):
        """Admin no puede eliminarse a sí mismo desde el panel admin."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('core:admin_usuario_eliminar', args=[self.admin_user.pk]))
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))
        self.assertTrue(User.objects.filter(pk=self.admin_user.pk).exists())

    @patch('certificados.file_handler.CertificadoFileHandler.delete_file')
    def test_admin_elimina_otro_usuario(self, mock_delete_file):
        """Admin puede eliminar a otro usuario y todos sus recursos asociados."""
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('core:admin_usuario_eliminar', args=[self.normal_user.pk]))
        self.assertRedirects(response, reverse('core:admin_usuario_lista'))
        self.assertFalse(User.objects.filter(pk=self.normal_user.pk).exists())
