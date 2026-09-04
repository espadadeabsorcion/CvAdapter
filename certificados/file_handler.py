import os
import uuid

from django.conf import settings

from .exceptions import (
    FileStorageError,
    FileTooLargeError,
    InvalidFileTypeError,
)


class CertificadoFileHandler:
    """
    Responsable de validar, guardar, localizar y eliminar los archivos PDF
    de los Certificados.
    """

    MAX_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE', 5 * 1024 * 1024)  # 5 MB
    ALLOWED_EXTENSIONS = {'.pdf'}
    ALLOWED_MIME_TYPES = {'application/pdf', 'application/x-pdf'}

    # ------------------------------------------------------------------ #
    # Configuración de directorios
    # ------------------------------------------------------------------ #
    @staticmethod
    def _upload_dir():
        """Retorna el directorio de subida configurado en settings.CV_UPLOAD_DIR."""
        return getattr(settings, 'CV_UPLOAD_DIR', None) or (
            settings.BASE_DIR / 'media' / 'certificados'
        )

    # ------------------------------------------------------------------ #
    # Validación
    # ------------------------------------------------------------------ #
    @classmethod
    def validate_file(cls, file):
        """
        Valida el tipo MIME, la extensión y el tamaño máximo del archivo.

        Lanza:
            - InvalidFileTypeError si la extensión o el MIME no son PDF.
            - FileTooLargeError si el tamaño supera los 5 MB.
        """
        name = getattr(file, 'name', '')

        # 1. Tamaño máximo
        size = getattr(file, 'size', 0)
        if size > cls.MAX_SIZE:
            raise FileTooLargeError()

        # 2. Extensión
        ext = os.path.splitext(name)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeError(
                'Solo se permiten archivos con extensión .pdf.'
            )

        # 3. Tipo MIME
        content_type = (getattr(file, 'content_type', '') or '').lower()
        if content_type and content_type not in cls.ALLOWED_MIME_TYPES:
            raise InvalidFileTypeError(
                'El tipo de archivo no es un documento PDF válido.'
            )

        return True

    # ------------------------------------------------------------------ #
    # Guardado
    # ------------------------------------------------------------------ #
    @classmethod
    def save_file(cls, file, instance):
        """
        Valida y guarda el archivo con un nombre interno único (UUID.pdf).

        Actualiza el Certificado con:
            - archivo_interno: nombre interno generado (UUID.pdf).
            - archivo_url: nombre original sanitizado (solo el nombre base).

        Retorna el nombre interno generado.
        """
        cls.validate_file(file)

        nombre_original = os.path.basename(getattr(file, 'name', ''))
        nombre_interno = f"{uuid.uuid4().hex}.pdf"

        upload_dir = cls._upload_dir()
        os.makedirs(upload_dir, exist_ok=True)

        path_destino = os.path.join(upload_dir, nombre_interno)
        try:
            with open(path_destino, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except OSError as exc:
            # Limpiar archivo parcial si falló la escritura
            if os.path.exists(path_destino):
                try:
                    os.remove(path_destino)
                except OSError:
                    pass
            raise FileStorageError() from exc

        instance.archivo_interno = nombre_interno
        instance.archivo_url = nombre_original
        return nombre_interno

    # ------------------------------------------------------------------ #
    # Localización
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_file_path(instance):
        """
        Retorna la ruta absoluta al archivo físico del Certificado.

        Retorna None si el certificado no tiene archivo_interno definido.
        """
        archivo_interno = getattr(instance, 'archivo_interno', None)
        if not archivo_interno:
            return None
        return os.path.join(
            CertificadoFileHandler._upload_dir(),
            instance.archivo_interno,
        )

    # ------------------------------------------------------------------ #
    # Eliminación
    # ------------------------------------------------------------------ #
    @classmethod
    def delete_file(cls, instance):
        """
        Elimina el archivo físico del Certificado si existe.

        Retorna True si el archivo fue eliminado, False si no existía.
        Nunca lanza excepción si el archivo no estaba presente.
        """
        path_archivo = cls.get_file_path(instance)
        if not path_archivo or not os.path.exists(path_archivo):
            return False

        try:
            os.remove(path_archivo)
        except OSError as exc:
            raise FileStorageError(
                'No fue posible eliminar el archivo físico del servidor.'
            ) from exc

        return True
