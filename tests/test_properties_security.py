# tests/test_properties_security.py
# Feature: cv-adaptable, Property 8: Los security headers están presentes en todas las respuestas HTTP
#
# Validates: Requirements 11.1

from django.test import Client
from django.contrib.auth.models import User
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase


MAIN_ENDPOINTS = [
    '/login/',
    '/dashboard/',
]

SECURITY_HEADERS = [
    ('X-Content-Type-Options', 'nosniff'),
    ('X-Frame-Options', 'DENY'),
    ('X-XSS-Protection', '1; mode=block'),
]


class SecurityHeadersPropertyTest(TestCase):
    """
    **Validates: Requirements 11.1**

    Property 8: Los security headers están presentes en todas las respuestas HTTP.

    Para cualquier endpoint del sistema (URL protegida, URL pública, respuesta de
    error), la respuesta HTTP producida por SecurityHeadersMiddleware debe contener
    exactamente los headers X-Content-Type-Options: nosniff, X-Frame-Options: DENY
    y X-XSS-Protection: 1; mode=block, independientemente del código de estado.
    """

    @given(url=st.sampled_from(MAIN_ENDPOINTS))
    @settings(max_examples=100)
    def test_security_headers_en_todas_las_respuestas(self, url):
        """
        Property 8: Para cualquier endpoint del sistema, la respuesta HTTP
        debe contener los 3 security headers, independientemente del código
        de estado (200, 302, 403, etc.).

        Se prueba sin sesión activa para obtener códigos de estado variados:
        - /login/ → 200 (página pública)
        - /dashboard/ → 302 (redirige a login porque no hay sesión)
        """
        client = Client()
        response = client.get(url)

        for header_name, expected_value in SECURITY_HEADERS:
            self.assertIn(
                header_name,
                response,
                f"Header '{header_name}' ausente en respuesta de {url} "
                f"(status {response.status_code})",
            )
            self.assertEqual(
                response[header_name],
                expected_value,
                f"Header '{header_name}' incorrecto en {url}: "
                f"esperado '{expected_value}', "
                f"obtenido '{response.get(header_name)}'",
            )

    @given(url=st.sampled_from(MAIN_ENDPOINTS))
    @settings(max_examples=100)
    def test_security_headers_con_usuario_autenticado(self, url):
        """
        Property 8 (variante autenticada): Las respuestas a un usuario con
        sesión activa también deben contener los 3 security headers.
        Cubre los endpoints protegidos que devuelven 200 en lugar de 302.
        """
        # get_or_create evita la colisión de username entre ejemplos de Hypothesis
        user, _ = User.objects.get_or_create(
            username='propuser8',
            defaults={'password': 'unusable'},
        )
        client = Client()
        client.force_login(user)
        response = client.get(url)

        for header_name, expected_value in SECURITY_HEADERS:
            self.assertIn(
                header_name,
                response,
                f"Header '{header_name}' ausente en respuesta autenticada de {url} "
                f"(status {response.status_code})",
            )
            self.assertEqual(
                response[header_name],
                expected_value,
                f"Header '{header_name}' incorrecto en respuesta autenticada de {url}: "
                f"esperado '{expected_value}', "
                f"obtenido '{response.get(header_name)}'",
            )
