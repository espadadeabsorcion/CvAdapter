# Estado Actual del Proyecto — CV Adaptable

> Documento de referencia sobre el estado real del código, en contraste con el
> plan de implementación (`/.kiro/specs/cv-adaptable/tasks.md`).

---

## 1. Resumen

**CV Adaptable** es una aplicación web **Django 6.0.5** (ejecutada con Python
3.14.7) para gestionar un perfil profesional único y generar CVs filtrados por
categorías profesionales. Está orientada a un único usuario (Lenin) con
despliegue previsto en PythonAnywhere.

La base de datos actual es **SQLite** (`db.sqlite3`) con DEBUG=True, es decir,
configuración de desarrollo. No existe separación `settings/base.py` /
`settings/development.py` / `settings/production.py` como plantea el plan; todo
vive en un único `cv_adaptable_project/settings.py`.

---

## 2. Estructura de Apps

| App | Rol principal | Estado |
|-----|---------------|--------|
| `core` | Login, logout, dashboard, middleware de seguridad | **Operativa** |
| `perfil` | Perfil, experiencia, educación, habilidades, idiomas (CRUD) | **Operativa** |
| `certificados` | Categorías y certificados PDF | **Operativa (parcial)** |
| `generador` | Selección de categorías y generación/vista previa del CV | **Operativa (parcial)** |

Rutas raíz (`cv_adaptable_project/urls.py`):
- `/admin/`, `/` (redirect según sesión), `/login/`, `/logout/`, `/dashboard/`
- `/perfil/...`, `/categorias/...` + `/certificados/...`, `/cv/...`

---

## 3. Modelos (migrados correctamente)

- **`perfil`**: `Perfil`, `Experiencia`, `Educacion`, `Habilidad`, `Idioma`
  - `Idioma.nivel` usa niveles CEFR (`A1`–`C2`) — NOTA: difiere de lo que pide
    el requirements (Básico/Intermedio/Avanzado/Nativo).
  - `Habilidad.tipo` distingue `hard` / `power`.
  - `Perfil.foto` (ImageField) + `foto_url` (redundancia).
- **`certificados`**: `Categoria` (FK a User, nombre único por usuario),
  `Certificado` (FK a Perfil, M2M a Categoria, `archivo_url` = nombre original,
  `archivo_interno` = nombre interno).
- Migraciones aplicadas y consistentes (`showmigrations` OK, incluye `axes`).

---

## 4. Seguridad

- `SecurityHeadersMiddleware` (`core/middleware.py`) añade
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `X-XSS-Protection: 1; mode=block` a toda respuesta (**Req. 11.1**).
- **django-axes**: 5 intentos fallidos / 15 min de bloqueo
  (`AXES_FAILURE_LIMIT`, `AXES_COOLOFF_TIME`).
- Sesión: `SESSION_COOKIE_AGE=28800` (8 h), HttpOnly, `SAVE_EVERY_REQUEST`.
- Aún no hay config de producción segura (DEBUG sigue en True, sin SSL/MySQL).

---

## 5. Funcionalidad Implementada

### `perfil` (CRUD completo)
- `PerfilView` (ver/editar, crea perfil si no existe), y List/Create/Update/Delete
  para `Experiencia`, `Educacion`, `Habilidad`, `Idioma`.
- Todos los Update/Delete filtran por `perfil__usuario=request.user` (ownership).
- Templates HTML presentes para todas las secciones.

### `certificados`
- CRUD de `Categoria` y `Certificado`.
- Descarga segura vía `CertificadoDownloadView` con ownership check (**Req. 11.3/11.4**).
- **Divergencia clave**: **NO existe** `certificados/file_handler.py`. La
  validación MIME/tamaño/extensión que debería estar en un `FileHandler`
  (tarea 7.1 del plan) **no está implementada**; la subida/borrado de archivos
  se maneja inline en las vistas (ej. `CertificadoDeleteView` y
  `CertificadoDownloadView` gestionan el path manualmente).

### `generador`
- `SeleccionarCategoriaView` y `GenerarCvView` (filtrado por categorías) y
  `PreviewCvView` (vista previa estándar).
- Uso de `perfil/repositories.py` (`get_*`) para las consultas.
- **Divergencia clave**: **NO existe** `generador/generator.py` (clase
  `CVGenerator`, tarea 9.1); la lógica está dentro de `GenerarCvView`.

---

## 6. Templates

Existen templates en `perfil/`, `certificados/`, `generador/` y `core/`
(incluido `base.html`). Según el plan, la tarea 11 (templates con firma visual
Bootstrap, `base_print.html`, estilos `.btn-cv-*`) figura como **`[~]` (sin
terminar)**. Actualmente `.prettierignore` excluye los `.html` de Prettier.

---

## 7. Tests (ESTADO ACTUAL: solo 2) — ⚠️ PENDIENTE

La suite `pytest` **colecciona y ejecuta únicamente 2 tests**:

- `tests/test_properties_security.py` → Property 8 (security headers) ✓
  (2 passed, 5.25s: variantes sin sesión y autenticada).

**NO existen aún** los tests unitarios ni el resto de property tests descritos
en el plan (Properties 1–7 y 9: filtrado, datos completos, rango de fechas,
unicidad, preservación de categorías, FileHandler, ownership).

Tampoco existe `tests/conftest.py` (fixtures `user`, `perfil`, `client`
autenticado) previsto en la tarea 13.2.

---

## 8. Divergencias respecto al plan de implementación

| Plan (tasks.md) | Estado real |
|-----------------|-------------|
| Split `settings/base.py` + dev/prod | ❌ Un solo `settings.py`; sin config de producción |
| `certificados/file_handler.py` (validate/store/serve/delete) | ❌ No existe; lógica inline |
| `generador/generator.py` (`CVGenerator`) | ❌ No existe; lógica en la vista |
| `tests/conftest.py` con fixtures | ❌ No existe |
| Suite completa de tests + property tests 1–7, 9 | ❌ Solo Property 8 (2 tests) |
| `NIVEL_CHOICES` = Básico/Intermedio/Avanzado/Nativo (Req. 6.5) | ⚠️ Usa CEFR A1–C2 |
| Templates con firma visual + `base_print.html` | ⚠️ Parcial, tarea 11 `[~]` |
| Config producción/despliegue PythonAnywhere (DEBUG=False, MySQL) | ❌ Pendiente |
| WhiteNoise para estáticos en producción | ❌ No configurado |

---

## 9. Próximos pasos evidentes

1. **Escribir el `FileHandler`** (`certificados/file_handler.py`) y enrutar la
   subida/borrado/descarga de certificados a través de él (reqs 7.1–7.4).
2. **Extraer `CVGenerator`** (`generador/generator.py`) de la vista
   `GenerarCvView` (reqs 10.2, 10.7).
3. **Ampliar la suite de tests**: unit tests por app + property tests 1–7 y 9;
   crear `tests/conftest.py`.
4. **Completar templates** con la firma visual y `base_print.html` (tarea 11).
5. **Configurar producción**: `settings` seguros (`DEBUG=False`, MySQL,
   `SECRET_KEY`/`DB_*` desde entorno), WhiteNoise, `.env.example`,
   `CV_UPLOAD_DIR` fuera de la raíz web (tarea 14).

---

## 10. Comandos útiles

```powershell
# Ejecutar la suite de tests
python -m pytest --tb=short

# Ver migraciones aplicadas
python manage.py showmigrations

# Arrancar el servidor de desarrollo
python manage.py runserver
```

---

_Generado el 2026-09-03. Estado correspondiente a la revisión del código actual._
