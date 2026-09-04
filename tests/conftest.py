import pytest
from django.contrib.auth.models import User
from django.test import Client

from certificados.models import Categoria
from perfil.models import Perfil


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def perfil(user):
    return Perfil.objects.create(
        usuario=user,
        nombre_completo="Juan Perez",
        email="juan@example.com",
        telefono="123456789",
        titulo_profesional="Ingeniero de Software",
        resumen_profesional="Desarrollador con 5 años de experiencia.",
    )


@pytest.fixture
def client_auth(user):
    client = Client()
    client.login(username="testuser", password="testpass123")
    return client


@pytest.fixture
def categoria(user):
    return Categoria.objects.create(
        usuario=user,
        nombre="Desarrollo Web",
        descripcion="Certificados de desarrollo web",
    )
