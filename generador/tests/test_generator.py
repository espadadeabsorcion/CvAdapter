import pytest
from django.contrib.auth.models import User

from certificados.models import Categoria, Certificado
from generador.generator import CVGenerator
from perfil.models import Habilidad, Perfil


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123')


@pytest.fixture
def perfil(user):
    return Perfil.objects.create(
        usuario=user,
        nombre_completo='Juan Pérez',
        email='juan@example.com',
        titulo_profesional='Desarrollador',
        resumen_profesional='Desarrollador backend.',
    )


@pytest.fixture
def categorias(perfil, user):
    cat_dev = Categoria.objects.create(usuario=user, nombre='Desarrollo Web')
    cat_rrhh = Categoria.objects.create(usuario=user, nombre='Recursos Humanos')
    return cat_dev, cat_rrhh


@pytest.fixture
def datos_con_categorias(perfil, categorias):
    """Crea habilidades y certificados repartidos entre las categorías."""
    cat_dev, cat_rrhh = categorias

    hab_python = Habilidad.objects.create(perfil=perfil, nombre='Python', tipo='hard', nivel=5)
    hab_python.categorias.add(cat_dev)

    hab_entrevista = Habilidad.objects.create(perfil=perfil, nombre='Entrevistas', tipo='power', nivel=4)
    hab_entrevista.categorias.add(cat_rrhh)

    cert_dev = Certificado.objects.create(
        perfil=perfil,
        nombre='Cert Django',
        archivo_interno='a.pdf',
        fecha_obtencion='2023-01-01',
    )
    cert_dev.categorias.add(cat_dev)

    cert_rrhh = Certificado.objects.create(
        perfil=perfil,
        nombre='Cert RRHH',
        archivo_interno='b.pdf',
        fecha_obtencion='2023-02-01',
    )
    cert_rrhh.categorias.add(cat_rrhh)

    return cat_dev, cat_rrhh


class TestFiltradoPorCategoria:
    def test_solo_incluye_habilidades_y_certificados_de_la_categoria(self, perfil, datos_con_categorias):
        cat_dev, _ = datos_con_categorias
        gen = CVGenerator(perfil=perfil, categorias_seleccionadas=[cat_dev])

        ctx = gen.get_context_data()

        nombres_hard = [h.nombre for h in ctx['habilidades_hard']]
        nombres_power = [h.nombre for h in ctx['habilidades_power']]
        todos_hard = nombres_hard + nombres_power

        assert 'Python' in todos_hard
        assert 'Entrevistas' not in todos_hard

        nombres_cert = [c.nombre for c in ctx['certificados']]
        assert 'Cert Django' in nombres_cert
        assert 'Cert RRHH' not in nombres_cert

    def test_sin_categorias_incluye_todo(self, perfil, datos_con_categorias):
        gen = CVGenerator(perfil=perfil, categorias_seleccionadas=[])

        ctx = gen.get_context_data()

        todos = [h.nombre for h in ctx['habilidades_hard']] + \
            [h.nombre for h in ctx['habilidades_power']]
        assert 'Python' in todos
        assert 'Entrevistas' in todos


class TestGeneracionHTML:
    def test_html_contiene_nombre_del_perfil(self, perfil):
        gen = CVGenerator(perfil=perfil)
        html = gen.generate_html()

        assert perfil.nombre_completo in html

    def test_generate_pdf_retorna_html(self, perfil):
        gen = CVGenerator(perfil=perfil)
        assert gen.generate_pdf() == gen.generate_html()


class TestPerfilSinDatos:
    def test_no_rompe_con_perfil_vacio(self, perfil):
        gen = CVGenerator(perfil=perfil)
        html = gen.generate_html()

        assert 'Juan Pérez' in html
        # El template maneja secciones vacías sin fallar
        assert html is not None and html != ''
