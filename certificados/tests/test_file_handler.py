import os

import pytest
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from certificados.exceptions import FileTooLargeError, InvalidFileTypeError
from certificados.file_handler import CertificadoFileHandler


def _nuevo_archivo(nombre, contenido, content_type):
    return SimpleUploadedFile(nombre, contenido, content_type=content_type)


class TestValidateFile:
    """Valida la lógica de validación de archivos."""

    def test_acepta_pdf_valido(self):
        archivo = _nuevo_archivo('certificado.pdf', b'%PDF-1.4', 'application/pdf')
        assert CertificadoFileHandler.validate_file(archivo) is True

    def test_rechaza_extension_no_pdf(self):
        archivo = _nuevo_archivo('documento.txt', b'hola', 'text/plain')
        with pytest.raises(InvalidFileTypeError):
            CertificadoFileHandler.validate_file(archivo)

    def test_rechaza_mime_no_pdf(self):
        archivo = _nuevo_archivo('certificado.pdf', b'%PDF-1.4', 'application/octet-stream')
        with pytest.raises(InvalidFileTypeError):
            CertificadoFileHandler.validate_file(archivo)

    def test_rechaza_archivo_mayor_a_5mb(self):
        contenido = b'x' * (5 * 1024 * 1024 + 1)
        archivo = _nuevo_archivo('grande.pdf', contenido, 'application/pdf')
        with pytest.raises(FileTooLargeError):
            CertificadoFileHandler.validate_file(archivo)


class DummyInstance:
    archivo_interno = None
    archivo_url = None


class TestSaveFile:
    """Valida el guardado del archivo con nombre UUID y escritura en disco."""

    def test_guarda_con_nombre_uuid_y_ruta_relativa(self):
        archivo = _nuevo_archivo('mi_cert.pdf', b'%PDF-1.4 contenido', 'application/pdf')
        instancia = DummyInstance()
        nombre_interno = CertificadoFileHandler.save_file(archivo, instancia)

        assert os.path.splitext(nombre_interno)[1] == '.pdf'
        # Nombre interno: 32 hex chars + .pdf
        assert len(nombre_interno) == 32 + 4

        ruta = os.path.join(settings.CV_UPLOAD_DIR, nombre_interno)
        assert os.path.exists(ruta)

        assert instancia.archivo_interno == nombre_interno
        assert instancia.archivo_url == 'mi_cert.pdf'

        os.remove(ruta)


class TestDeleteFile:
    """Valida la eliminación del archivo físico."""

    def test_elimina_archivo_fisico(self):
        archivo = _nuevo_archivo('borrar.pdf', b'%PDF-1.4', 'application/pdf')
        instancia = DummyInstance()
        CertificadoFileHandler.save_file(archivo, instancia)
        ruta = os.path.join(settings.CV_UPLOAD_DIR, instancia.archivo_interno)
        assert os.path.exists(ruta)

        resultado = CertificadoFileHandler.delete_file(instancia)
        assert resultado is True
        assert not os.path.exists(ruta)

    def test_no_lanza_error_si_archivo_no_existe(self):
        instancia = DummyInstance()
        instancia.archivo_interno = 'no_existe.pdf'
        assert CertificadoFileHandler.delete_file(instancia) is False

    def test_no_op_sin_archivo_interno(self):
        instancia = DummyInstance()
        assert CertificadoFileHandler.delete_file(instancia) is False


class TestGetFilePath:
    """Valida la localización de la ruta absoluta del archivo."""

    def test_retorna_ruta_absoluta(self):
        instancia = DummyInstance()
        instancia.archivo_interno = 'abc123.pdf'
        ruta = CertificadoFileHandler.get_file_path(instancia)
        assert ruta == os.path.join(settings.CV_UPLOAD_DIR, 'abc123.pdf')

    def test_retorna_none_sin_archivo(self):
        instancia = DummyInstance()
        assert CertificadoFileHandler.get_file_path(instancia) is None
