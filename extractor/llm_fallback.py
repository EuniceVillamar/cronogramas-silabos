"""IA de respaldo para extracciones de baja confianza. Pendiente para la semana 4.

Una fecha propuesta por la IA solo se acepta si su texto aparece en el PDF.
"""

from .models import ActividadExtraida, DocumentoPDF


def extraer_con_ia(documento: DocumentoPDF) -> list[ActividadExtraida]:
    raise NotImplementedError
