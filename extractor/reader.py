"""Lectura de texto y tablas de un PDF."""

from pathlib import Path
from typing import BinaryIO

import pdfplumber

from .models import DocumentoPDF, PaginaPDF


def leer_pdf(origen: str | Path | BinaryIO) -> DocumentoPDF:
    with pdfplumber.open(origen) as pdf:
        return DocumentoPDF(paginas=tuple(_leer_pagina(pagina) for pagina in pdf.pages))


def _leer_pagina(pagina) -> PaginaPDF:
    tablas = tuple(
        tuple(tuple(celda or "" for celda in fila) for fila in tabla)
        for tabla in pagina.extract_tables()
    )
    return PaginaPDF(numero=pagina.page_number, texto=pagina.extract_text() or "", tablas=tablas)
