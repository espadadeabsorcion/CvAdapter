from django.core.exceptions import ValidationError


class InvalidFileTypeError(ValidationError):
    """Se lanza cuando el archivo no es un PDF válido."""

    def __init__(self, message='Solo se permiten archivos PDF.'):
        super().__init__(message)


class FileTooLargeError(ValidationError):
    """Se lanza cuando el archivo supera el tamaño máximo permitido."""

    def __init__(self, message='El archivo excede el tamaño máximo permitido de 5MB.'):
        super().__init__(message)


class FileStorageError(ValidationError):
    """Se lanza cuando falla una operación de lectura/escritura del archivo."""

    def __init__(self, message='No fue posible procesar el archivo en el servidor.'):
        super().__init__(message)
