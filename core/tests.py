"""
core/tests.py

Unit tests para autenticación, middleware de seguridad y comportamiento de sesión.

Requisitos cubiertos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 11.1
"""

from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse


# ---------------------------------------------------------------------------
# Configuración base para tests de axes (necesita resetear contadores entre
# tests para evitar interferencias). Override de axes para tests de bloqueo.
# ---------------------------------------------------------------------------

@override_settings(
    AXES_ENABLED=True,
    AXES_FAILURE_LIMIT=5,
    AXES_COOLOFF_TIME=0.25,
    AXES_LOCKOUT_PARAMETERS=['username'],
)
class AuthTests(TestCase):
    """Tests unitarios para las vistas de autenticación (Req. 1.1–1.7)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # Cliente sin CSRF enforcement para la mayoría de los tests
        self.client = Client(enforce_csrf_checks=False)

    # ------------------------------------------------------------------
    # Req. 1.1 — Credenciales válidas crean sesión y redirigen al dashboard
    # ------------------------------------------------------------------
    def test_login_credenciales_validas_redirige_dashboard(self):
        """POST con credenciales válidas → 302 a /dashboard/."""
        response = self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertRedirects(response, '/dashboard/')

    def test_login_credenciales_validas_crea_sesion(self):
        """Tras login exitoso la sesión queda autenticada."""
        # Usar POST al login (flujo real) para verificar que la sesión se crea
        self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        # Verificar que el usuario autenticado puede acceder al dashboard
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)

    # ------------------------------------------------------------------
    # Req. 1.2 — Credenciales inválidas muestran mensaje genérico
    # ------------------------------------------------------------------
    def test_login_credenciales_invalidas_mensaje_generico(self):
        """POST con contraseña incorrecta → 200 con mensaje genérico."""
        response = self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'wrongpass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')

    def test_login_usuario_inexistente_mensaje_generico(self):
        """POST con usuario inexistente → mismo mensaje genérico (sin revelar detalle)."""
        response = self.client.post(
            reverse('core:login'),
            {'username': 'noexiste', 'password': 'cualquierpass'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos.')

    def test_login_credenciales_invalidas_no_revela_campo_erroneo(self):
        """El mensaje de error no indica si fue el usuario o la contraseña."""
        response = self.client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'wrongpass'}
        )
        content = response.content.decode()
        # No debe haber mensajes que revelen qué campo es incorrecto
        self.assertNotIn('contraseña incorrecta', content.lower())
        self.assertNotIn('usuario incorrecto', content.lower())
        self.assertNotIn('password is wrong', content.lower())

    # ------------------------------------------------------------------
    # Req. 1.3 — 5 intentos fallidos bloquean la cuenta
    # ------------------------------------------------------------------
    def test_cinco_intentos_fallidos_bloquean_cuenta(self):
        """Después de 5 intentos fallidos, el 6to queda bloqueado (axes devuelve 429, 403 o 200)."""
        login_url = reverse('core:login')

        # 5 intentos fallidos
        for _ in range(5):
            self.client.post(
                login_url,
                {'username': 'testuser', 'password': 'wrongpass'}
            )

        # 6to intento — aunque la contraseña sea correcta, debe estar bloqueado
        response = self.client.post(
            login_url,
            {'username': 'testuser', 'password': 'testpass123'}
        )
        # axes puede devolver 429 (Too Many Requests), 403 (Forbidden) o
        # una página de bloqueo con 200 según la configuración
        self.assertIn(
            response.status_code,
            [429, 403, 200],
            msg="El 6to intento tras 5 fallidos debe retornar 429, 403 o página de bloqueo (200)."
        )
        # Si devuelve 200, la respuesta no debe ser una redirección al dashboard
        if response.status_code == 200:
            self.assertNotIn(
                response.get('Location', ''),
                ['/dashboard/'],
                msg="Una cuenta bloqueada no debe redirigir al dashboard."
            )

    def test_cuatro_intentos_fallidos_no_bloquean(self):
        """4 intentos fallidos no deben bloquear la cuenta todavía."""
        login_url = reverse('core:login')

        for _ in range(4):
            self.client.post(
                login_url,
                {'username': 'testuser', 'password': 'wrongpass'}
            )

        # El 5to intento con contraseña correcta aún debe funcionar
        # (el bloqueo ocurre después del 5to intento fallido, no antes)
        response = self.client.post(
            login_url,
            {'username': 'testuser', 'password': 'testpass123'}
        )
        # Debe redirigir al dashboard (cuenta no bloqueada aún)
        self.assertRedirects(response, '/dashboard/')

    # ------------------------------------------------------------------
    # Req. 1.4 — Logout destruye la sesión y redirige al login
    # ------------------------------------------------------------------
    def test_logout_destruye_sesion_redirige_login(self):
        """POST a /logout/ destruye la sesión y redirige a /login/."""
        # Usar force_login para no pasar por el backend de axes
        self.client.force_login(self.user)

        # Cerrar sesión
        response = self.client.post(reverse('core:logout'))
        self.assertRedirects(response, '/login/')

    def test_logout_invalida_sesion_activa(self):
        """Después del logout, acceder a ruta protegida redirige al login."""
        self.client.force_login(self.user)

        # Verificar que el dashboard es accesible antes del logout
        resp_antes = self.client.get(reverse('core:dashboard'))
        self.assertEqual(resp_antes.status_code, 200)

        # Hacer logout
        self.client.post(reverse('core:logout'))

        # El dashboard ya no debe ser accesible
        resp_despues = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(
            resp_despues,
            '/login/?next=/dashboard/',
            msg_prefix="Tras logout, el dashboard debe redirigir al login con ?next="
        )

    # ------------------------------------------------------------------
    # Req. 1.5 — Rutas protegidas sin sesión redirigen al login con ?next
    # ------------------------------------------------------------------
    def test_ruta_protegida_sin_sesion_redirige_login_con_next(self):
        """GET a /dashboard/ sin sesión → 302 a /login/?next=/dashboard/."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_ruta_raiz_sin_sesion_redirige_login(self):
        """GET a / sin sesión → redirige a /login/."""
        response = self.client.get('/')
        self.assertRedirects(response, '/login/')

    def test_ruta_raiz_con_sesion_redirige_dashboard(self):
        """GET a / con sesión activa → redirige a /dashboard/."""
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertRedirects(response, '/dashboard/')

    def test_usuario_autenticado_en_login_redirige_dashboard(self):
        """Si ya está autenticado, GET /login/ redirige a /dashboard/."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:login'))
        self.assertRedirects(response, '/dashboard/')

    # ------------------------------------------------------------------
    # Req. 1.6 — CSRF token presente en el formulario de login
    # ------------------------------------------------------------------
    def test_csrf_token_presente_en_formulario_login(self):
        """GET /login/ → el HTML contiene el token CSRF."""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    # ------------------------------------------------------------------
    # Req. 1.7 — CSRF inválido/ausente retorna 403
    # ------------------------------------------------------------------
    def test_csrf_invalido_retorna_403(self):
        """POST sin CSRF token válido → 403 Forbidden."""
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------------
    # Req. 11.1 — Security headers presentes en todas las respuestas
    # ------------------------------------------------------------------
    def test_security_headers_presentes_en_login_page(self):
        """GET /login/ → los 3 security headers tienen los valores correctos."""
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

    def test_security_headers_presentes_en_respuesta_invalida(self):
        """POST con CSRF inválido (403) → los headers de seguridad siguen presentes."""
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(
            reverse('core:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

    def test_security_headers_presentes_en_dashboard(self):
        """GET /dashboard/ (autenticado) → los 3 security headers presentes."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')


class SecurityHeadersMiddlewareTests(TestCase):
    """Tests directos sobre SecurityHeadersMiddleware (Req. 11.1)."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_headers_presentes_en_get_login(self):
        """GET /login/ siempre incluye los 3 security headers."""
        response = self.client.get(reverse('core:login'))
        self.assertIn('X-Content-Type-Options', response)
        self.assertIn('X-Frame-Options', response)
        self.assertIn('X-XSS-Protection', response)

    def test_header_x_content_type_options_valor(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_header_x_frame_options_valor(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response['X-Frame-Options'], 'DENY')

    def test_header_x_xss_protection_valor(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')

    def test_headers_en_redirect_sin_sesion(self):
        """Una respuesta 302 (sin sesión) también lleva los headers de seguridad."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-XSS-Protection'], '1; mode=block')
