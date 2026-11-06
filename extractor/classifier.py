"""Detección del formato del cronograma. Pendiente para la semana 2."""

from .models import DocumentoPDF, FormatoSilabo


def detectar_formato(documento: DocumentoPDF) -> FormatoSilabo:
    raise NotImplementedError
