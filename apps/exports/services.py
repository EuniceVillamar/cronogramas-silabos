"""Une el extractor con la exportación: de los PDF a la planificación y el .ics."""

import logging

from pdfminer.pdfparser import PDFSyntaxError

from apps.exports.ics import generar_ics
from extractor.calendario import extraer_calendario
from extractor.planificacion import Planificacion, planificar
from extractor.silabo import extraer_silabo

logger = logging.getLogger(__name__)


class ArchivoIlegible(Exception):
    """El PDF no se pudo leer o no tiene el formato esperado."""


def generar_planificacion(calendario, silabos, dias_repaso: int) -> tuple[Planificacion, bytes]:
    try:
        datos_calendario = extraer_calendario(calendario)
    except (PDFSyntaxError, ValueError) as error:
        raise ArchivoIlegible(f"No pude leer el calendario {_nombre(calendario)}.") from error
    if not datos_calendario.eventos:
        raise ArchivoIlegible(
            f"{_nombre(calendario)} no parece un calendario académico: no encontré fechas."
        )

    extraidos = []
    avisos = []
    for silabo in silabos:
        try:
            extraido = extraer_silabo(silabo)
        except (PDFSyntaxError, ValueError):
            logger.warning("No se pudo leer el sílabo %s", _nombre(silabo), exc_info=True)
            avisos.append(f"No pude leer el sílabo {_nombre(silabo)}; se omitió.")
            continue
        if not extraido.unidades:
            avisos.append(f"{_nombre(silabo)} no parece un sílabo: no encontré unidades.")
            continue
        extraidos.append(extraido)

    plan = planificar(datos_calendario, extraidos, dias_repaso=dias_repaso)
    plan.advertencias = avisos + plan.advertencias
    return plan, generar_ics(plan)


def _nombre(archivo) -> str:
    return getattr(archivo, "name", str(archivo))
