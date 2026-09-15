from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from certificados.models import Categoria, Certificado
from perfil.models import Perfil, Habilidad


class GeneradorCvTests(TestCase):
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
        self.cat_dev = Categoria.objects.create(usuario=self.user, nombre='Desarrollo Web')
        self.cat_rrhh = Categoria.objects.create(usuario=self.user, nombre='Recursos Humanos')

        self.hab_python = Habilidad.objects.create(perfil=self.perfil, nombre='Python', nivel=5)
        self.hab_python.categorias.add(self.cat_dev)

        self.hab_entrevista = Habilidad.objects.create(perfil=self.perfil, nombre='Entrevistas de Selección', nivel=4)
        self.hab_entrevista.categorias.add(self.cat_rrhh)

    def test_generar_cv_filtrado_por_categoria(self):
        """Verifica que el CV generado solo contenga las habilidades asociadas a la categoría elegida."""
        response = self.client.get(reverse('generador:cv_adaptado'), {'categorias': [self.cat_dev.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertNotContains(response, 'Entrevistas de Selección')

    def test_generar_cv_completo_sin_filtro(self):
        """Verifica que sin categoría seleccionada se muestren todas las habilidades."""
        response = self.client.get(reverse('generador:cv_adaptado'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Entrevistas de Selección')


class CVPublicoTests(TestCase):
    """El CV público es accesible sin autenticación y multi-usuario por username."""

    def setUp(self):
        self.user = User.objects.create_user(username='lenin', password='password123')
        self.perfil = Perfil.objects.create(
            usuario=self.user,
            nombre_completo='Lenin Ramírez',
            email='lenin@example.com',
            telefono='+593991234567',
            titulo_profesional='HR Specialist',
            resumen_profesional='Experto en desarrollo organizacional'
        )
        self.cat_dev = Categoria.objects.create(usuario=self.user, nombre='Desarrollo Web')
        self.cat_rrhh = Categoria.objects.create(usuario=self.user, nombre='Recursos Humanos')

        self.hab_python = Habilidad.objects.create(perfil=self.perfil, nombre='Python', nivel=5)
        self.hab_python.categorias.add(self.cat_dev)

        self.hab_entrevista = Habilidad.objects.create(perfil=self.perfil, nombre='Entrevistas de Selección', nivel=4)
        self.hab_entrevista.categorias.add(self.cat_rrhh)

    def test_cv_publico_accesible_sin_autenticacion(self):
        """Un visitante anónimo debe poder ver el CV público por username."""
        response = self.client.get(reverse('cv_publico', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lenin Ramírez')
        self.assertContains(response, 'HR Specialist')

    def test_cv_publico_por_defecto(self):
        """Sin username en la URL se publica el primer perfil activo."""
        response = self.client.get(reverse('cv_publico_por_defecto'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lenin Ramírez')

    def test_cv_publico_muestra_todas_las_categorias(self):
        """El CV público incluye habilidades de TODAS las categorías (sin filtrado)."""
        response = self.client.get(reverse('cv_publico', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python')
        self.assertContains(response, 'Entrevistas de Selección')

    def test_cv_publico_aislado_por_usuario(self):
        """El CV de un usuario NO debe filtrar datos de otro usuario."""
        otro_user = User.objects.create_user(username='maria', password='password123')
        Perfil.objects.create(
            usuario=otro_user,
            nombre_completo='María Pérez',
            email='maria@example.com',
            titulo_profesional='Data Analyst',
            resumen_profesional='Otra persona',
        )
        Habilidad.objects.create(perfil=otro_user.perfil, nombre='SQL', nivel=5)

        response = self.client.get(reverse('cv_publico', args=[self.user.username]))
        self.assertContains(response, 'Lenin Ramírez')
        self.assertContains(response, 'Python')
        self.assertNotContains(response, 'SQL')
        self.assertNotContains(response, 'María Pérez')

    def test_cv_publico_404_username_inexistente(self):
        """Un username sin perfil público devuelve 404."""
        response = self.client.get(reverse('cv_publico', args=['no_existe']))
        self.assertEqual(response.status_code, 404)

    def test_cv_publico_404_con_perfil_inactivo(self):
        """Un perfil desactivado deja de estar disponible públicamente."""
        self.perfil.is_active = False
        self.perfil.save()
        response = self.client.get(reverse('cv_publico', args=[self.user.username]))
        self.assertEqual(response.status_code, 404)

    def test_cv_publico_404_sin_perfil(self):
        """Sin perfiles activos la vista pública debe devolver 404."""
        self.perfil.delete()
        response = self.client.get(reverse('cv_publico', args=[self.user.username]))
        self.assertEqual(response.status_code, 404)
