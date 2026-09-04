# Requirements Document

## Introduction

**CV Adaptable** es un sistema web desarrollado en Django que permite al usuario mantener un perfil profesional único y generar versiones personalizadas del CV según el área o industria a la que aplica. El sistema elimina el trabajo repetitivo de re-formatear el mismo CV para distintos puestos, ofreciendo un mecanismo de categorización que filtra y exporta únicamente los elementos relevantes para cada oportunidad laboral.

El sistema está orientado a un único usuario (Lenin) en un entorno de hosting compartido económico (PythonAnywhere o similar), con un MVP funcional en 3 días de desarrollo.

---

## Glossary

- **Sistema**: La aplicación web CV Adaptable construida con Django 4.x.
- **Usuario**: El profesional autenticado (Lenin) que gestiona su perfil y genera CVs.
- **Perfil**: El conjunto completo de datos profesionales del Usuario almacenados en la base de datos.
- **Experiencia**: Un registro de empleo previo o actual con empresa, cargo, fechas y descripción.
- **Educacion**: Un registro académico con institución, título, fechas y descripción.
- **Habilidad**: Una competencia técnica o blanda del Usuario representada como etiqueta (tag).
- **Idioma**: Un idioma hablado por el Usuario con su nivel de dominio.
- **Certificado**: Un archivo PDF subido por el Usuario que acredita una formación o logro.
- **Categoria**: Una agrupación temática personalizada (ej: "Desarrollo Web") que el Usuario crea para clasificar Habilidades y Certificados.
- **CV_Generado**: El documento HTML imprimible producido por el Generador a partir de una selección de Categorias.
- **Generador**: El componente del Sistema responsable de producir el CV_Generado.
- **Validator**: El componente del Sistema responsable de validar entradas de formulario en el lado del servidor.
- **FileHandler**: El componente del Sistema responsable de recibir, validar y almacenar archivos subidos.
- **Autenticador**: El componente del Sistema que gestiona el acceso mediante credenciales de usuario Django.

---

## Requirements

### Requerimiento 1: Autenticación de Usuario

**User Story:** Como usuario, quiero iniciar y cerrar sesión de forma segura, para que solo yo pueda acceder y modificar mi información profesional.

#### Criterios de Aceptación

1. WHEN el Usuario envía credenciales válidas en el formulario de login, THE Autenticador SHALL crear una sesión autenticada con duración máxima de 8 horas de inactividad y redirigir al dashboard principal en menos de 3 segundos.
2. IF el Usuario envía credenciales inválidas, THEN THE Autenticador SHALL mostrar un mensaje de error genérico sin revelar si el usuario o contraseña es incorrecto, e incrementar un contador de intentos fallidos para esa cuenta.
3. IF el contador de intentos fallidos para una cuenta alcanza 5 intentos consecutivos, THEN THE Autenticador SHALL bloquear el acceso a esa cuenta durante 15 minutos y mostrar un mensaje indicando el bloqueo temporal.
4. WHEN el Usuario solicita cerrar sesión, THE Autenticador SHALL destruir la sesión activa, invalidar el token de sesión del lado del servidor y redirigir a la página de login.
5. WHILE el Usuario no tiene una sesión autenticada activa, THE Sistema SHALL redirigir cualquier solicitud a rutas protegidas hacia la página de login, preservando la URL solicitada originalmente como parámetro de redirección.
6. THE Sistema SHALL incluir un token CSRF en el formulario de login para proteger contra ataques de falsificación de solicitudes entre sitios.
7. IF el token CSRF del formulario de login no es válido o está ausente, THEN THE Sistema SHALL rechazar la solicitud de autenticación y mostrar un mensaje de error indicando que la solicitud no pudo procesarse.

---

### Requerimiento 2: Gestión del Perfil Profesional

**User Story:** Como usuario, quiero mantener un perfil profesional completo con mis datos personales, para que el Sistema pueda usarlos como base al generar cualquier versión del CV.

#### Criterios de Aceptación

1. THE Sistema SHALL presentar un formulario de perfil con los campos obligatorios: nombre completo (máximo 100 caracteres), email (máximo 254 caracteres, formato válido de correo electrónico), teléfono (máximo 20 caracteres), título profesional (máximo 100 caracteres) y resumen profesional (máximo 1000 caracteres).
2. WHEN el Usuario envía el formulario de perfil con todos los campos obligatorios completos y válidos, THE Sistema SHALL guardar o actualizar el Perfil en la base de datos y mostrar un mensaje de confirmación visible en pantalla en un máximo de 3 segundos.
3. IF el Usuario envía el formulario de perfil con uno o más campos obligatorios vacíos, THEN THE Validator SHALL mostrar un mensaje de error específico por campo vacío sin borrar los datos ingresados en los demás campos.
4. IF el Usuario ingresa un valor con formato inválido en algún campo del formulario de perfil (por ejemplo, un email sin el símbolo @), THEN THE Validator SHALL mostrar un mensaje de error específico por campo con formato inválido sin borrar los datos ingresados en los demás campos.
5. IF el Usuario ingresa un email que no cumple el formato de dirección de correo electrónico válida (usuario@dominio.extensión), THEN THE Validator SHALL mostrar un mensaje de error indicando que el campo email requiere una dirección de correo válida.
6. WHEN el Usuario accede a la vista del Perfil y ya existe un Perfil guardado, THE Sistema SHALL cargar el formulario con los valores actuales del Perfil en un máximo de 3 segundos.
7. THE Sistema SHALL sanitizar todos los campos de texto del formulario de perfil antes de persistir los datos en la base de datos para prevenir la inyección de código malicioso.
8. THE Sistema SHALL incluir un token CSRF en el formulario de perfil.

---

### Requerimiento 3: Gestión de Experiencia Laboral

**User Story:** Como usuario, quiero registrar múltiples experiencias laborales, para que el CV refleje mi trayectoria profesional completa o filtrada.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir al Usuario crear, editar y eliminar registros de Experiencia de forma independiente sin afectar otros registros de Experiencia existentes.
2. WHEN el Usuario crea o edita una Experiencia, THE Validator SHALL requerir los campos empresa (máximo 100 caracteres), cargo (máximo 100 caracteres) y fecha de inicio como obligatorios antes de guardar.
3. WHEN el Usuario guarda una Experiencia con todos los campos obligatorios válidos, THE Sistema SHALL asociar el registro de Experiencia al Perfil del Usuario autenticado y mostrar la Experiencia actualizada en la lista dentro de los 2 segundos siguientes.
4. IF el Usuario deja vacío uno o más campos obligatorios (empresa, cargo o fecha de inicio) al guardar una Experiencia, THEN THE Validator SHALL mostrar un mensaje de error indicando qué campos son requeridos y retener los valores ingresados en el formulario.
5. IF el Usuario ingresa una fecha de fin anterior a la fecha de inicio en una Experiencia, THEN THE Validator SHALL mostrar un mensaje de error indicando que el rango de fechas es inválido y retener los valores ingresados en el formulario.
6. THE Sistema SHALL presentar la lista de Experiencias ordenada por fecha de inicio de forma descendente (la más reciente primero).
7. THE Sistema SHALL incluir un token CSRF en los formularios de creación y edición de Experiencia.
8. WHEN el Usuario confirma la eliminación de una Experiencia, THE Sistema SHALL eliminar únicamente ese registro y reflejar la lista actualizada dentro de los 2 segundos siguientes.

---

### Requerimiento 4: Gestión de Educación

**User Story:** Como usuario, quiero registrar mis títulos y formaciones académicas, para que el CV incluya mi historial educativo relevante.

#### Criterios de Aceptación

1. WHEN el Usuario crea un registro de Educacion, THE Sistema SHALL crear el registro de forma independiente sin modificar ni eliminar otros registros de Educacion existentes del mismo Perfil.
2. WHEN el Usuario edita un registro de Educacion, THE Sistema SHALL actualizar únicamente el registro seleccionado sin modificar otros registros de Educacion existentes del mismo Perfil.
3. WHEN el Usuario elimina un registro de Educacion, THE Sistema SHALL eliminar únicamente el registro seleccionado sin modificar otros registros de Educacion existentes del mismo Perfil.
4. WHEN el Usuario intenta guardar un registro de Educacion con el campo institución vacío o con más de 200 caracteres, THE Validator SHALL rechazar el guardado y mostrar un mensaje de error indicando que el campo institución es obligatorio y tiene un límite de 200 caracteres.
5. WHEN el Usuario intenta guardar un registro de Educacion con el campo título obtenido vacío o con más de 200 caracteres, THE Validator SHALL rechazar el guardado y mostrar un mensaje de error indicando que el campo título obtenido es obligatorio y tiene un límite de 200 caracteres.
6. WHEN el Usuario intenta guardar un registro de Educacion con el campo fecha de inicio vacío o con un valor que no corresponde a una fecha válida en formato YYYY-MM-DD, THE Validator SHALL rechazar el guardado y mostrar un mensaje de error indicando que la fecha de inicio es obligatoria y debe ser una fecha válida.
7. IF el Usuario ingresa una fecha de fin en el registro de Educacion y dicha fecha es anterior a la fecha de inicio, THEN THE Validator SHALL rechazar el guardado y mostrar un mensaje de error indicando que la fecha de fin no puede ser anterior a la fecha de inicio.
8. WHEN el Usuario guarda un registro de Educacion válido, THE Sistema SHALL asociar el registro al Perfil del Usuario autenticado activo en la sesión.
9. IF el Usuario intenta guardar un registro de Educacion sin una sesión autenticada activa, THEN THE Sistema SHALL rechazar la operación y redirigir al Usuario a la página de inicio de sesión sin guardar el registro.
10. THE Sistema SHALL presentar la lista de registros de Educacion del Perfil ordenada por fecha de inicio de forma descendente, mostrando los registros con fecha de inicio más reciente primero.
11. THE Sistema SHALL incluir un token CSRF en los formularios de creación y edición de Educacion, y rechazar cualquier solicitud de guardado que no incluya un token CSRF válido.

---

### Requerimiento 5: Gestión de Habilidades

**User Story:** Como usuario, quiero registrar mis habilidades como etiquetas y asignarlas a categorías, para que el Generador pueda filtrar las habilidades relevantes según el área del CV.

#### Criterios de Aceptación

1. THE Sistema SHALL permitir al Usuario crear, editar y eliminar registros de Habilidad representados como etiquetas de texto.
2. WHEN el Usuario crea una Habilidad, THE Validator SHALL requerir que el nombre de la Habilidad tenga entre 1 y 100 caracteres y sea único por Usuario (sin distinción de mayúsculas y minúsculas).
3. WHEN el Usuario edita una Habilidad, THE Validator SHALL requerir que el nombre actualizado tenga entre 1 y 100 caracteres y sea único por Usuario excluyendo el registro editado.
4. IF la validación del nombre de la Habilidad falla (vacío, supera 100 caracteres o está duplicado), THEN THE Validator SHALL mostrar un mensaje de error específico indicando la causa y no persistir ningún cambio.
5. WHEN el Usuario crea una Habilidad, THE Sistema SHALL permitir asignar la Habilidad a cero o más Categorias existentes mediante selección múltiple.
6. WHEN el Usuario edita una Habilidad, THE Sistema SHALL permitir agregar o quitar asociaciones con Categorias existentes sin afectar otras Habilidades.
7. WHEN el Usuario elimina una Categoria, THE Sistema SHALL mantener los registros de Habilidad existentes y solo remover la asociación con la Categoria eliminada.
8. WHEN el Usuario confirma la eliminación de una Habilidad, THE Sistema SHALL eliminar el registro de Habilidad y remover todas sus asociaciones con Categorias sin afectar los registros de Categorias.
9. THE Sistema SHALL incluir un token CSRF en los formularios de creación y edición de Habilidad.

---

### Requerimiento 6: Gestión de Idiomas

**User Story:** Como usuario, quiero registrar los idiomas que manejo con su nivel de dominio, para que el CV muestre mis competencias lingüísticas.

#### Criterios de Aceptación

1. WHEN el Usuario solicita crear un registro de Idioma, THE Sistema SHALL mostrar un formulario con los campos nombre del idioma y nivel de dominio.
2. WHEN el Usuario solicita editar un registro de Idioma existente, THE Sistema SHALL mostrar un formulario con los campos nombre del idioma y nivel de dominio precargados con los valores actuales del registro.
3. WHEN el Usuario solicita eliminar un registro de Idioma, THE Sistema SHALL eliminar el registro y reflejar el cambio en la lista de idiomas del CV sin requerir recarga manual de la página.
4. WHEN el Usuario envía el formulario de creación o edición de Idioma, THE Validator SHALL verificar que el campo nombre del idioma no esté vacío y no exceda 100 caracteres; IF la validación falla, THEN THE Sistema SHALL mostrar un mensaje de error indicando el campo inválido y conservar los valores ingresados sin guardar el registro.
5. THE Sistema SHALL ofrecer exactamente los niveles de dominio: Básico, Intermedio, Avanzado y Nativo como opciones seleccionables para el campo nivel de dominio, sin permitir valores distintos a esos cuatro.
6. THE Sistema SHALL incluir un token CSRF en los formularios de creación y edición de Idioma, rechazando el envío con un error de validación si el token está ausente o no es válido.

---

### Requerimiento 7: Gestión de Certificados

**User Story:** Como usuario, quiero subir mis certificados en PDF y asociarlos a categorías, para que el Generador incluya los certificados relevantes en cada versión del CV.

#### Criterios de Aceptación

1. WHEN el Usuario sube un archivo, THE FileHandler SHALL aceptar únicamente archivos con tipo MIME pplication/pdf y extensión .pdf, con un tamaño máximo de 5 MB y un nombre de archivo de máximo 255 caracteres.
2. IF el Usuario intenta subir un archivo con tipo MIME distinto a pplication/pdf o extensión distinta a .pdf, THEN THE FileHandler SHALL rechazar el archivo y mostrar un mensaje de error indicando que solo se permiten archivos PDF.
3. IF el Usuario intenta subir un archivo con tamaño superior a 5 MB, THEN THE FileHandler SHALL rechazar el archivo y mostrar un mensaje de error indicando el límite de tamaño.
4. WHEN el FileHandler acepta y valida un archivo PDF, THE Sistema SHALL almacenar el archivo en el sistema de archivos del servidor fuera del directorio de archivos estáticos y fuera del directorio raíz web, asignando un nombre de archivo interno generado por el sistema que no exponga el nombre original.
5. WHILE el Usuario accede a la sección de Certificados, THE Sistema SHALL presentar la lista de Certificados subidos mostrando el nombre de archivo original, la fecha de subida en formato DD/MM/YYYY HH:MM, y una opción para eliminar cada Certificado.
6. WHEN el Usuario elimina un Certificado, THE Sistema SHALL eliminar el registro de la base de datos y el archivo físico del sistema de archivos del servidor de forma atómica; IF la operación falla en cualquiera de los dos pasos, THEN THE Sistema SHALL revertir ambos cambios y mostrar un mensaje de error indicando que el Certificado no pudo eliminarse.
7. WHEN el Usuario sube un Certificado, THE Sistema SHALL permitir asignar el Certificado a cero o más Categorías existentes mediante selección múltiple de las Categorías disponibles en el sistema.
8. IF el Usuario intenta subir un Certificado y no existe ninguna Categoría registrada en el sistema, THEN THE Sistema SHALL permitir continuar la subida sin asignar Categorías, mostrando un aviso indicando que no hay Categorías disponibles.
9. THE Sistema SHALL incluir un token CSRF en el formulario de subida de Certificados y rechazar cualquier solicitud de subida que no incluya un token CSRF válido mostrando un mensaje de error indicando que la solicitud no es válida.

---

### Requerimiento 8: Gestión de Categorías

**User Story:** Como usuario, quiero crear y administrar categorías personalizadas, para que pueda organizar mis habilidades y certificados según el área profesional a la que aplico.

#### Criterios de Aceptación

1. WHEN el Usuario solicita crear una Categoria, THE Sistema SHALL crear el registro de Categoria con el nombre proporcionado y asociarlo al Usuario autenticado activo en la sesión.
2. WHEN el Usuario solicita editar una Categoria, THE Sistema SHALL actualizar únicamente el nombre del registro de Categoria seleccionado sin modificar otras Categorias existentes.
3. WHEN el Usuario solicita eliminar una Categoria, THE Sistema SHALL eliminar el registro de Categoria del sistema y desasociar la Categoria de todas las Habilidades y Certificados relacionados sin eliminar esos registros.
4. WHEN el Usuario crea o edita una Categoria, THE Validator SHALL requerir que el nombre de la Categoria tenga entre 1 y 100 caracteres.
5. IF el Usuario intenta crear una Categoria con un nombre idéntico (ignorando mayúsculas y minúsculas) a una Categoria existente del mismo Usuario, THEN THE Validator SHALL rechazar la creación y mostrar un mensaje de error indicando que el nombre ya existe.
6. WHEN el Usuario accede a la sección de Categorias, THE Sistema SHALL presentar la lista de Categorias del Usuario autenticado con el conteo de Habilidades y Certificados asociados a cada una.
7. IF la eliminación de una Categoria falla en cualquier paso de la operación, THEN THE Sistema SHALL revertir todos los cambios parciales y mostrar un mensaje de error indicando que la Categoria no pudo eliminarse, preservando intactos el registro de Categoria y todas sus asociaciones existentes.
8. THE Sistema SHALL incluir un token CSRF en los formularios de creación y edición de Categoria.

---

### Requerimiento 9: Vista Previa del CV Estándar

**User Story:** Como usuario, quiero ver una vista previa de mi CV completo en formato estándar, para que pueda revisar que toda mi información está correcta antes de generar una versión filtrada.

#### Criterios de Aceptación

1. WHEN el Usuario accede a la vista previa estándar, THE Sistema SHALL renderizar todos los datos del Perfil, Experiencias, Educacion, Habilidades, Idiomas y Certificados del Usuario autenticado en una plantilla HTML imprimible; IF alguna sección no tiene registros, THEN THE Sistema SHALL mostrar un mensaje indicando que no hay datos disponibles para esa sección en lugar de omitir la sección.
2. IF el Usuario accede a la vista previa estándar sin una sesión autenticada activa, THEN THE Sistema SHALL redirigir al Usuario a la página de inicio de sesión sin renderizar datos del Perfil.
3. WHILE el Usuario visualiza la vista previa estándar, THE Sistema SHALL presentar las secciones con delimitación visual entre ellas, en el orden: Datos Personales, Resumen Profesional, Experiencia Laboral (orden cronológico descendente), Educación (orden cronológico descendente), Habilidades, Idiomas y Certificados, aplicando el gradiente de header azul (#11cdef → #1171ef) y los colores de la firma visual del desarrollador.
4. THE Sistema SHALL presentar la vista previa estándar en un formato optimizado para impresión en papel A4, suprimiendo elementos de navegación (menús, botones, encabezados del sitio) al imprimir y aplicando una anchura máxima de 210 mm en el CSS de impresión.

---

### Requerimiento 10: Generación de CV por Categoría

**User Story:** Como usuario, quiero seleccionar una o más categorías y generar un CV que solo incluya los elementos de esas categorías, para que pueda adaptar mi presentación profesional a cada oportunidad laboral sin esfuerzo manual.

#### Criterios de Aceptación

1. WHEN el Usuario accede al Generador, THE Sistema SHALL presentar la lista completa de Categorias disponibles con controles de selección múltiple, mostrando el nombre de cada Categoria y el conteo de Habilidades y Certificados asociados.
2. WHEN el Usuario selecciona una o más Categorias y solicita la generación, THE Generador SHALL producir un CV_Generado en un máximo de 3 segundos que incluya únicamente las Habilidades y Certificados asignados a las Categorias seleccionadas, junto con todos los datos del Perfil, Experiencias, Educacion e Idiomas del Usuario.
3. IF el Usuario solicita la generación sin seleccionar ninguna Categoria, THEN THE Generador SHALL mostrar un mensaje de error indicando que debe seleccionar al menos una Categoria, preservando el estado actual de la selección.
4. WHEN el Generador produce el CV_Generado, THE Sistema SHALL renderizar el CV_Generado como una página HTML imprimible con las secciones en el orden: Datos Personales, Resumen Profesional, Experiencia Laboral, Educación, Habilidades filtradas, Idiomas y Certificados filtrados, aplicando la firma visual del desarrollador.
5. WHEN el CV_Generado está disponible, THE Sistema SHALL presentar un botón de impresión visible sin necesidad de hacer scroll que ejecute window.print() directamente desde el navegador.
6. THE CV_Generado SHALL ser compatible con los navegadores Chrome, Firefox y Edge en sus versiones actuales.
7. IF el Generador no puede recuperar los datos del Usuario durante la generación, THEN THE Sistema SHALL mostrar un mensaje de error indicando que no fue posible generar el CV y no renderizar una página parcial.

---

### Requerimiento 11: Seguridad General del Sistema

**User Story:** Como usuario, quiero que el sistema proteja mis datos y archivos de accesos no autorizados, para que mi información profesional permanezca privada y segura.

#### Criterios de Aceptación

1. THE Sistema SHALL configurar los headers de seguridad HTTP X-Content-Type-Options: nosniff, X-Frame-Options: DENY y X-XSS-Protection: 1; mode=block en todas las respuestas HTTP, independientemente del código de estado de la respuesta.
2. IF el Usuario no tiene una sesión autenticada activa, THEN THE Sistema SHALL redirigir la solicitud a la vista de login sin procesar la acción solicitada, aplicando esta verificación a todas las vistas excepto la vista de login.
3. WHEN el Sistema recibe una solicitud para servir un archivo Certificado, THE Sistema SHALL verificar que el identificador del Usuario autenticado coincide con el identificador del propietario registrado del Certificado antes de entregar el archivo.
4. IF el Usuario autenticado no es el propietario del Certificado solicitado, THEN THE Sistema SHALL rechazar la entrega del archivo y retornar una respuesta de acceso denegado sin revelar la existencia o ruta del archivo.
5. THE Sistema SHALL operar con DEBUG = False en el entorno de producción, retornando al Usuario final una página de error genérica sin trazas de ejecución, nombres de módulos internos ni rutas del sistema de archivos ante cualquier error no controlado.
6. THE Sistema SHALL cargar la SECRET_KEY de Django y las credenciales de la base de datos exclusivamente desde variables de entorno del sistema operativo, de forma que el repositorio de código fuente no contenga ninguno de estos valores en texto plano.
