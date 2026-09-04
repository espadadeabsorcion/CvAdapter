# Implementation Plan: CV Adaptable

## Overview

Implementación incremental de la aplicación web Django para gestión de perfil profesional y generación de CVs filtrados por categoría. El plan sigue el orden: setup del proyecto → modelos → seguridad → CRUD por app → templates → tests → despliegue.

Cada tarea produce código funcional e integrado; no hay código huérfano entre pasos.

---

## Tasks

- [~] 1. Configuración inicial del proyecto Django y estructura de apps

  - Crear el proyecto Django con `django-admin startproject cv_adaptable_project .`
  - Crear las cuatro apps: `python manage.py startapp core`, `perfil`, `certificados`, `generador`
  - Configurar `settings/base.py` con `INSTALLED_APPS`, `TEMPLATES`, `STATIC_URL`, `MEDIA_URL`, zona horaria `America/Guayaquil` y codificación UTF-8
  - Crear `settings/development.py` (DEBUG=True, SQLite) y `settings/production.py` (DEBUG=False, MySQL, vars de entorno)
  - Leer `SECRET_KEY`, `DB_*` exclusivamente desde `os.environ` en `production.py`
  - Configurar `SESSION_COOKIE_AGE = 28800`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True` en `production.py`
  - Instalar dependencias: `Django>=4.2`, `mysqlclient`, `python-magic`, `django-axes`, `hypothesis`, `pytest-django`, `whitenoise`; fijar versiones exactas en `requirements.txt`
  - Crear `manage.py` apuntando a `settings.development` por defecto; definir variable de entorno `DJANGO_SETTINGS_MODULE`
  - Crear estructura de directorios: `templates/`, `static/css/`, `static/js/`, `cv_uploads/` (fuera de raíz web)
  - _Requirements: 11.5, 11.6_

- [x] 2. Modelos de datos y migraciones

  - [x] 2.1 Implementar modelos de la app `perfil`
    - Escribir `Perfil`, `Experiencia`, `Educacion`, `Habilidad`, `Idioma` en `perfil/models.py` según el diseño
    - Añadir `clean()` con validación de rango de fechas en `Experiencia` y `Educacion`
    - Definir `UniqueConstraint(perfil, nombre)` en `Habilidad`
    - Definir `ordering = ['-fecha_inicio']` en `Experiencia` y `Educacion`
    - Definir `NIVEL_CHOICES` con exactamente: Básico, Intermedio, Avanzado, Nativo en `Idioma`
    - Registrar todos los modelos en `perfil/admin.py`
    - _Requirements: 3.6, 4.10, 5.2, 6.5_

  - [x] 2.2 Implementar modelos de la app `certificados`
    - Escribir `Categoria` con `UniqueConstraint(usuario, nombre)` y FK a `auth.User` en `certificados/models.py`
    - Escribir `Certificado` con campos `archivo_url` (nombre original), `archivo_interno` (UUID), FK a `perfil.Perfil`, M2M a `Categoria`
    - Registrar modelos en `certificados/admin.py`
    - _Requirements: 7.4, 8.1, 8.5_

  - [x] 2.3 Generar y aplicar migraciones
    - Ejecutar `makemigrations` para `perfil` y `certificados`; revisar el SQL generado
    - Ejecutar `migrate` con la base de datos de desarrollo (SQLite)
    - Verificar que las constraints `unique_habilidad_perfil` y `unique_categoria_usuario` aparecen en el esquema
    - _Requirements: 5.2, 8.5_

- [x] 3. Autenticación, middleware de seguridad y configuración de django-axes

  - [x] 3.1 Implementar `SecurityHeadersMiddleware` y configuración de seguridad
    - Escribir `core/middleware.py` con `SecurityHeadersMiddleware` que añade `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block` a toda respuesta
    - Registrar el middleware en `MIDDLEWARE` de `settings/base.py` en la posición correcta (antes de `SessionMiddleware`)
    - Configurar `django-axes` en `MIDDLEWARE` después de `AuthenticationMiddleware`, y los parámetros `AXES_FAILURE_LIMIT=5`, `AXES_COOLOFF_TIME=0.25`, `AXES_LOCKOUT_PARAMETERS=['username']` en `settings/base.py`
    - _Requirements: 1.3, 11.1_

  - [x] 3.2 Implementar vistas de autenticación en `core`
    - Crear `core/urls.py` con rutas `/login/` y `/logout/`
    - Subclasificar `LoginView` de Django para mostrar mensaje genérico en credenciales inválidas (`get_form_kwargs` / `form_invalid`)
    - Configurar `LOGIN_URL`, `LOGIN_REDIRECT_URL = '/dashboard/'`, `LOGOUT_REDIRECT_URL = '/login/'` en settings
    - Implementar `DashboardView(LoginRequiredMixin, TemplateView)` en `core/views.py`
    - Añadir ruta raíz `/` con redirect condicional (autenticado → dashboard, sin sesión → login)
    - Incluir CSRF token en el template de login
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.6, 1.7_

  - [x] 3.3 Escribir unit tests para autenticación y middleware
    - `test_login_credenciales_validas_redirige_dashboard`
    - `test_login_credenciales_invalidas_mensaje_generico`
    - `test_cinco_intentos_fallidos_bloquean_cuenta`
    - `test_logout_destruye_sesion_redirige_login`
    - `test_csrf_invalido_retorna_403`
    - `test_ruta_protegida_sin_sesion_redirige_login_con_next`
    - `test_security_headers_presentes_en_login_page`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [x] 3.4 Escribir property test — Property 8: Security headers en todas las respuestas
    - **Property 8: Los security headers están presentes en todas las respuestas HTTP**
    - Usar `@given(url=st.sampled_from([...]))` con los endpoints principales
    - Verificar los 3 headers en cada respuesta independientemente del código de estado
    - **Validates: Requirements 11.1**

- [~] 4. Checkpoint — Autenticación y seguridad base funcionan
  - Verificar que el login/logout opera correctamente, los headers aparecen, y django-axes bloquea tras 5 intentos. Preguntar al usuario si hay dudas antes de continuar.

- [ ] 5. App `perfil` — ModelForms, CBVs y URLs

  - [x] 5.1 Implementar formularios de la app `perfil`
    - Crear `perfil/forms.py` con `PerfilForm(ModelForm)` para los campos: nombre_completo, email, telefono, titulo_profesional, resumen_profesional; aplicar `clean()` server-side para sanitizar con `bleach` o `strip_tags`
    - Crear `ExperienciaForm(ModelForm)` con validación de rango de fechas en `clean()` que llama `instance.clean()`
    - Crear `EducacionForm(ModelForm)` con la misma validación de rango
    - Crear `HabilidadForm(ModelForm)` con validación case-insensitive de unicidad usando `iexact` en `clean_nombre()`; aceptar `perfil` como parámetro en `__init__`
    - Crear `IdiomaForm(ModelForm)` restringiendo `nivel` al `choices` definido en el modelo
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.7, 3.2, 3.4, 3.5, 4.4, 4.5, 4.6, 4.7, 5.2, 5.3, 5.4, 6.4, 6.5_

  - [-] 5.2 Implementar CBVs y URLs del `Perfil`
    - Escribir `ProfileUpdateView(LoginRequiredMixin, UpdateView)` con `get_object()` que retorna `get_object_or_404(Perfil, usuario=request.user)` o crea un Perfil vacío si no existe
    - Definir `success_url` que redirige a la misma vista con mensaje de confirmación vía `messages`
    - Registrar URL `/perfil/` en `perfil/urls.py`
    - _Requirements: 2.2, 2.3, 2.6_

  - [-] 5.3 Implementar CBVs y URLs de `Experiencia`
    - Escribir `ExperienciaListView`, `ExperienciaCreateView`, `ExperienciaUpdateView`, `ExperienciaDeleteView` todos con `LoginRequiredMixin`
    - En `CreateView.form_valid()` asignar `form.instance.perfil = get_object_or_404(Perfil, usuario=request.user)`
    - En `UpdateView` y `DeleteView` filtrar el queryset por `perfil__usuario=request.user` para prevenir acceso cruzado
    - Registrar URLs en `perfil/urls.py`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [-] 5.4 Implementar CBVs y URLs de `Educacion`
    - Mismo patrón que Experiencia: List, Create, Update, Delete con ownership check en queryset
    - Asignar `perfil` en `form_valid()`, aplicar `ExperienciaForm`-equivalente para `EducacionForm`
    - Registrar URLs en `perfil/urls.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11_

  - [-] 5.5 Implementar CBVs y URLs de `Habilidad`
    - Escribir List, Create, Update, Delete con ownership via `perfil__usuario=request.user`
    - En `CreateView.get_form_kwargs()` pasar `perfil` al `HabilidadForm` para la validación case-insensitive
    - Incluir selección M2M de `Categorias` existentes del usuario en el formulario (widget `CheckboxSelectMultiple`)
    - Registrar URLs en `perfil/urls.py`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9_

  - [-] 5.6 Implementar CBVs y URLs de `Idioma`
    - Escribir List, Create, Update, Delete; validar nivel dentro de `NIVEL_CHOICES`
    - Registrar URLs en `perfil/urls.py`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [~] 5.7 Escribir unit tests para la app `perfil`
    - `test_perfil_carga_datos_existentes`
    - `test_perfil_campo_obligatorio_vacio_muestra_error_especifico`
    - `test_experiencia_lista_con_datos_vacios`
    - `test_educacion_independencia_crud`
    - `test_idioma_nivel_invalido_rechazado`
    - `test_habilidad_eliminacion_no_afecta_categorias`
    - `test_ownership_update_delete_bloquea_acceso_cruzado`
    - _Requirements: 2.2, 2.3, 3.1, 4.2, 4.3, 5.8, 6.4_

  - [~] 5.8 Escribir property test — Property 3: Validación de rango de fechas
    - **Property 3: Validación de rango de fechas es consistente para Experiencia y Educación**
    - `test_rango_fechas_consistente_experiencia` con `@given(fecha_inicio, fecha_fin)`
    - `test_rango_fechas_consistente_educacion` con `@given(fecha_inicio, fecha_fin)`
    - Si `fecha_fin < fecha_inicio` → form inválido con error en `fecha_fin`; si no → sin error de rango
    - **Validates: Requirements 3.5, 4.7**

  - [~] 5.9 Escribir property test — Property 4: Unicidad de nombres case-insensitive
    - **Property 4: Validación de nombres únicos rechaza duplicados ignorando capitalización**
    - `test_habilidad_duplicada_case_insensitive_rechazada` con `@given(nombre_base=st.text(...))`
    - `test_categoria_duplicada_case_insensitive_rechazada` con `@given(nombre_base=st.text(...))`
    - **Validates: Requirements 5.2, 5.3, 8.5**

- [~] 6. Checkpoint — CRUD de perfil completo funciona
  - Verificar que perfil, experiencias, educaciones, habilidades e idiomas se crean, editan y eliminan correctamente con los mensajes esperados. Preguntar al usuario si hay dudas.

- [ ] 7. App `certificados` — FileHandler, Categorías y Certificados

  - [~] 7.1 Implementar `FileHandler`
    - Crear `certificados/file_handler.py` con los métodos `validate()`, `store()`, `serve()`, `delete()` según el diseño
    - `validate()` verifica extensión `.pdf`, tamaño ≤ 5 MB y tipo MIME `application/pdf` usando `python-magic`; lanza `ValidationError` con mensaje específico en cada caso
    - `store()` llama `validate()`, genera nombre interno `UUID.pdf`, escribe en `UPLOAD_DIR` (configurado via `settings.CV_UPLOAD_DIR`), retorna el nombre interno
    - `serve()` retorna `FileResponse` con `content_type='application/pdf'`
    - `delete()` elimina el archivo físico solo si existe
    - `UPLOAD_DIR` debe apuntar a un directorio fuera de la raíz web; definir `CV_UPLOAD_DIR` en settings
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [~] 7.2 Implementar CBVs y URLs de `Categoria`
    - Crear `CategoriaForm(ModelForm)` en `certificados/forms.py` con validación case-insensitive de nombre único por usuario en `clean_nombre()`
    - Escribir `CategoriaListView` que anota cada categoría con `Count('habilidades') + Count('certificados')` mediante `annotate()`
    - Escribir `CategoriaCreateView`, `CategoriaUpdateView`, `CategoriaDeleteView`
    - En `CreateView.form_valid()` asignar `form.instance.usuario = request.user`
    - En `DeleteView.delete()` envolver en `transaction.atomic()` para garantizar atomicidad; capturar excepciones y mostrar error si falla
    - Registrar URLs `/categorias/...` en `certificados/urls.py`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [~] 7.3 Implementar CBVs y URLs de `Certificado` con `CertificadoServeView`
    - Crear `CertificadoForm(ModelForm)` con campo `archivo` de tipo `FileField`; la validación MIME/ext/tamaño ocurre en `FileHandler.validate()` llamado desde `clean_archivo()`
    - Mostrar aviso en el template si no hay categorías disponibles (Req. 7.8)
    - Escribir `CertificadoListView` (lista con nombre original, fecha formateada DD/MM/YYYY HH:MM, botón eliminar)
    - Escribir `CertificadoCreateView` donde `form_valid()` llama `FileHandler.store()` y asigna `archivo_interno` y `archivo_url` (nombre original sanitizado)
    - Escribir `CertificadoDeleteView` con eliminación atómica: `transaction.atomic()` + `cert.delete()` + `FileHandler.delete()`; revertir y mostrar error si falla cualquiera de los dos pasos
    - Escribir `CertificadoServeView(LoginRequiredMixin, View)` con `get()`: obtener certificado, verificar `cert.perfil.usuario == request.user` (lanzar `PermissionDenied` si no), retornar `FileHandler.serve()`
    - Registrar URLs `/certificados/...` incluyendo `/certificados/archivo/<pk>/`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 11.3, 11.4_

  - [~] 7.4 Escribir unit tests para `certificados`
    - `test_certificado_sin_categorias_disponibles_permite_subida`
    - `test_certificado_eliminacion_atomica_rollback_si_falla_disco`
    - `test_ownership_propietario_recibe_archivo`
    - `test_ownership_no_propietario_recibe_403`
    - `test_categoria_lista_muestra_conteos_correctos`
    - `test_categoria_eliminacion_desasocia_habilidades_y_certificados`
    - _Requirements: 7.6, 7.8, 8.3, 8.6, 11.3, 11.4_

  - [~] 7.5 Escribir property test — Property 5: Eliminar Categoría preserva elementos asociados
    - **Property 5: Eliminar una Categoría preserva todos los elementos asociados y solo remueve la asociación**
    - `test_eliminar_categoria_preserva_elementos_asociados` con `@given(n_habilidades, n_certificados)`
    - Verificar que las habilidades y certificados persisten y que ninguno mantiene la asociación con la categoría eliminada
    - **Validates: Requirements 5.7, 5.8, 8.3**

  - [~] 7.6 Escribir property tests — Properties 6 y 7: FileHandler
    - **Property 6: El FileHandler rechaza cualquier archivo que no sea PDF válido o exceda el tamaño máximo**
    - `test_filehandler_rechaza_extension_invalida` con `@given(contenido, extension=st.sampled_from(['.doc', ...]))`
    - `test_filehandler_rechaza_archivos_mayores_5mb` con `@given(extra_bytes=st.integers(min_value=1, ...))`
    - **Validates: Requirements 7.1, 7.2, 7.3**
    - **Property 7: El nombre de archivo almacenado es siempre un UUID distinto al nombre original**
    - `test_filehandler_genera_nombre_interno_uuid` con `@given(nombre_original=st.text(...).map(lambda s: s + '.pdf'))`
    - Verificar que el nombre interno termina en `.pdf` y su stem es un UUID válido (`uuid.UUID(nombre[:-4])`)
    - **Validates: Requirements 7.4**

  - [~] 7.7 Escribir property test — Property 9: Ownership check deniega acceso a no propietarios
    - **Property 9: El ownership check deniega el acceso a archivos de usuarios no propietarios**
    - `test_ownership_deniega_acceso_no_propietario` con `@given(user1_id, user2_id)` en rangos distintos
    - Verificar que `GET /certificados/archivo/<pk>/` por U2 retorna HTTP 403
    - **Validates: Requirements 11.3, 11.4**

- [~] 8. Checkpoint — App certificados completa con ownership y atomicidad
  - Verificar que el upload, listing, serving y eliminación atómica de certificados funcionan; que el ownership check retorna 403 correctamente. Preguntar al usuario si hay dudas.

- [ ] 9. App `generador` — CVGenerator, vista previa y generación filtrada

  - [~] 9.1 Implementar `CVGenerator`
    - Crear `generador/generator.py` con `CVGenerator.generate(user, categorias_ids)` según el diseño
    - Consultar `perfil`, `habilidades` (filtradas por categorías con `distinct()`), `certificados` (ídem), `experiencias` (order `-fecha_inicio`), `educaciones` (order `-fecha_inicio`), `idiomas`
    - Si `Perfil.objects.get()` lanza `Perfil.DoesNotExist`, propagar la excepción para que la vista la capture y muestre error sin renderizar parcial
    - _Requirements: 10.2, 10.7_

  - [~] 9.2 Implementar `CVPreviewView` (vista previa estándar)
    - Crear `CVPreviewView(LoginRequiredMixin, TemplateView)` en `generador/views.py`
    - En `get_context_data()` recuperar todos los datos del usuario sin filtro; si una sección está vacía pasar lista vacía (el template mostrará el mensaje)
    - Registrar URL `/cv/preview/`
    - _Requirements: 9.1, 9.2_

  - [~] 9.3 Implementar `CVGeneradorView` con formulario de selección
    - Crear `CategoriaSeleccionForm` en `generador/forms.py` con `ModelMultipleChoiceField` de `Categoria` filtrado por `request.user`; mostrar nombre y conteos via `queryset` anotado
    - Escribir `CVGeneradorView(LoginRequiredMixin, FormView)` con `form_valid()` que llama `CVGenerator.generate()`, captura excepciones y renderiza `cv_generado.html`
    - En `form_invalid()` o si no se selecciona ninguna categoría, re-renderizar `generador.html` con mensaje de error (Req. 10.3)
    - Registrar URL `/cv/generar/`
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [~] 9.4 Escribir unit tests para el generador
    - `test_cv_preview_sin_datos_muestra_mensajes_por_seccion`
    - `test_generador_sin_seleccion_muestra_error`
    - `test_cv_generado_orden_secciones`
    - `test_generador_fallo_datos_no_renderiza_parcial`
    - _Requirements: 9.1, 10.3, 10.4, 10.7_

  - [~] 9.5 Escribir property test — Property 1: Filtrado exacto por categorías
    - **Property 1: Filtrado de CV produce exactamente los elementos de las categorías seleccionadas**
    - `test_filtrado_cv_habilidades_exactas` con `@given(categorias_disponibles, seleccion)`
    - Verificar que `resultado['habilidades']` coincide exactamente con las habilidades cuyas categorías intersectan la selección
    - **Validates: Requirements 10.2**

  - [~] 9.6 Escribir property test — Property 2: Datos no filtrados siempre completos
    - **Property 2: El CV_Generado siempre incluye la totalidad de los datos no filtrados**
    - `test_cv_incluye_datos_no_filtrados_completos` con `@given(n_experiencias, n_educaciones, n_idiomas, seleccion_ids)`
    - Verificar que perfil, experiencias, educaciones e idiomas retornados coinciden con todos los registros del usuario
    - **Validates: Requirements 10.2**

- [~] 10. Checkpoint — Generador de CV completo
  - Verificar que la vista previa estándar y la generación filtrada funcionan con datos reales. Preguntar al usuario si hay dudas.

- [ ] 11. Templates HTML con firma visual

  - [~] 11.1 Crear `base.html` y `base_print.html`
    - Escribir `templates/base.html` con Bootstrap 5 CDN, header con `linear-gradient(135deg, #11cdef 0%, #1171ef 100%)`, navbar con logout, bloque `{% block content %}`
    - Definir clase `.btn-cv-primary` con `linear-gradient(135deg, #11f577 0%, #0ba85d 100%)` y `.btn-cv-secondary` con `linear-gradient(135deg, #a855f7 0%, #ec4899 100%)` en `static/css/cv_styles.css`
    - Escribir `templates/base_print.html` extendiendo `base.html`: sin nav, `@media print` con `max-width: 210mm`, supresión de botones y menús al imprimir
    - Incluir bloque `{% block extra_js %}` para jQuery Validate en vistas de formulario
    - _Requirements: 9.3, 9.4, 10.4_

  - [~] 11.2 Crear templates de `core` (login y dashboard)
    - `core/login.html`: formulario con `{% csrf_token %}`, validación jQuery Validate para campos requeridos, feedback visual de errores; badges de error con estilo semántico
    - `core/dashboard.html`: tarjetas de acceso rápido a cada sección con botones `.btn-cv-primary`
    - _Requirements: 1.6, 1.7_

  - [~] 11.3 Crear templates de `perfil`
    - `perfil/perfil_form.html`: formulario con jQuery Validate (campos obligatorios, formato email, límites de caracteres)
    - `perfil/experiencia_list.html` y `perfil/experiencia_form.html`: lista con DataTable hover effects, formulario con validación de fechas client-side
    - `perfil/educacion_list.html` y `perfil/educacion_form.html`: mismo patrón
    - `perfil/habilidad_list.html` y `perfil/habilidad_form.html`: badges de categoría asociadas, checkboxes para selección M2M
    - `perfil/idioma_list.html` y `perfil/idioma_form.html`: select restringido a 4 niveles
    - _Requirements: 2.1, 2.2, 2.3, 3.2, 4.4, 5.5, 6.1, 6.2_

  - [~] 11.4 Crear templates de `certificados`
    - `certificados/certificado_list.html`: nombre original, fecha `DD/MM/YYYY HH:MM`, botón eliminar `.btn-cv-secondary`; aviso si no hay categorías
    - `certificados/certificado_form.html`: campo file con indicación de tipos y límite; selección M2M de categorías
    - `certificados/categoria_list.html`: nombre + conteo de habilidades y certificados con badges de estado
    - `certificados/categoria_form.html`: formulario simple con validación jQuery Validate
    - _Requirements: 7.5, 7.8, 8.6_

  - [~] 11.5 Crear templates del `generador` (cv_preview, generador, cv_generado)
    - `generador/generador.html`: checkboxes de categorías con nombre y conteos; botón `.btn-cv-primary` para generar; mensaje de error si ninguna seleccionada
    - `generador/cv_preview.html` (extiende `base_print.html`): secciones Datos Personales → Resumen → Experiencia → Educación → Habilidades → Idiomas → Certificados; mensaje de "sin datos" por sección si está vacía; delimitación visual entre secciones con gradiente de header
    - `generador/cv_generado.html` (extiende `base_print.html`): mismo orden de secciones pero con habilidades y certificados filtrados; botón de impresión flotante que ejecuta `window.print()` visible sin scroll; compatible con Chrome, Firefox y Edge actuales
    - _Requirements: 9.1, 9.3, 9.4, 10.1, 10.4, 10.5, 10.6_

- [~] 12. Checkpoint — Templates y firma visual completos
  - Revisar visualmente login, dashboard, lista de experiencias, lista de categorías, vista previa y CV generado. Verificar que el botón de imprimir aparece sin scroll y que la impresión suprime el nav. Preguntar al usuario si hay ajustes de diseño.

- [ ] 13. Wiring: URLconf raíz y configuración final de apps

  - [~] 13.1 Conectar todas las apps en el URLconf raíz
    - Editar `cv_adaptable_project/urls.py`: incluir `core.urls`, `perfil.urls`, `certificados.urls`, `generador.urls` con sus prefijos correspondientes
    - Configurar el manejo de archivos estáticos con WhiteNoise en `MIDDLEWARE` para producción
    - Verificar que la ruta raíz `/` redirige correctamente según estado de autenticación
    - Verificar que `LOGIN_URL = '/login/'` está operativo y preserva el parámetro `?next=`
    - _Requirements: 1.5, 11.2_

  - [~] 13.2 Configurar `pytest.ini` / `conftest.py` y ejecutar suite completa
    - Crear `pytest.ini` con `DJANGO_SETTINGS_MODULE = cv_adaptable_project.settings.development`, `python_files = tests/test_*.py`
    - Crear `tests/conftest.py` con fixtures: `user`, `perfil`, `client` autenticado
    - Ejecutar `pytest --tb=short` y corregir cualquier fallo antes de continuar
    - _Requirements: (todos — verificación de integración)_

- [ ] 14. Configuración de despliegue en PythonAnywhere

  - [~] 14.1 Preparar archivos de configuración para producción
    - Crear `.env.example` con las variables requeridas: `DJANGO_SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `CV_UPLOAD_DIR`; asegurarse de que `.env` está en `.gitignore`
    - Verificar `settings/production.py`: `DEBUG=False`, `ALLOWED_HOSTS` con el dominio de PythonAnywhere, MySQL, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
    - Crear `wsgi.py` apuntando a `settings.production` cuando `DJANGO_SETTINGS_MODULE` está definido en el entorno
    - Documentar en comentarios de `settings/production.py` las variables de entorno que deben configurarse en la consola de PythonAnywhere
    - _Requirements: 11.5, 11.6_

  - [~] 14.2 Verificar configuración de archivos estáticos y uploads
    - Ejecutar `collectstatic` y verificar que WhiteNoise sirve los archivos correctamente
    - Confirmar que `CV_UPLOAD_DIR` apunta fuera de la raíz web del servidor y que el directorio existe con permisos de escritura
    - Verificar que el archivo `media` de certificados no es accesible directamente por URL, solo a través de `CertificadoServeView`
    - _Requirements: 7.4, 11.3_

- [~] 15. Checkpoint final — Suite completa de tests pasa
  - Ejecutar `pytest --tb=short` y confirmar que todos los tests unitarios y de propiedades pasan. Preguntar al usuario si hay ajustes finales antes de despliegue.

---

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido, pero son necesarias para garantizar las propiedades de corrección definidas en el diseño.
- Cada property test referencia explícitamente la propiedad del diseño que verifica.
- El orden de implementación sigue dependencias reales: los modelos deben existir antes de los formularios, los formularios antes de las vistas, las vistas antes de los templates.
- Los checkpoints son puntos de integración donde se debe verificar manualmente el estado del sistema antes de continuar.
- `django-axes` requiere su propia migración (`python manage.py migrate axes`); incluirla en el paso 3.1.
- El campo `nivel` en `Habilidad` (1–5) es para uso interno; en los templates se puede mostrar como estrellas o barra de progreso.
- La eliminación atómica de `Certificado` (tarea 7.3) debe usar `transaction.atomic()` envolviendo tanto `cert.delete()` como `FileHandler.delete()`; si `FileHandler.delete()` falla, el `atomic()` hace rollback del DELETE en DB.

---

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["2.1", "2.2"] },
    { "id": 1, "tasks": ["2.3"] },
    { "id": 2, "tasks": ["3.1", "3.2"] },
    { "id": 3, "tasks": ["3.3", "3.4", "5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3", "5.4", "5.5", "5.6"] },
    { "id": 5, "tasks": ["5.7", "5.8", "5.9", "7.1"] },
    { "id": 6, "tasks": ["7.2", "7.3"] },
    { "id": 7, "tasks": ["7.4", "7.5", "7.6", "7.7", "9.1"] },
    { "id": 8, "tasks": ["9.2", "9.3"] },
    { "id": 9, "tasks": ["9.4", "9.5", "9.6", "11.1"] },
    { "id": 10, "tasks": ["11.2", "11.3", "11.4"] },
    { "id": 11, "tasks": ["11.5", "13.1"] },
    { "id": 12, "tasks": ["13.2"] },
    { "id": 13, "tasks": ["14.1", "14.2"] }
  ]
}
```
