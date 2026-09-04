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
