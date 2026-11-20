"""Exportación de la planificación a iCalendar (.ics), compatible con Google y Outlook."""

import hashlib
from datetime import UTC, datetime, timedelta

from icalendar import Alarm, Calendar, Event

from extractor.planificacion import Planificacion

PRODID = "-//cronogramas-silabos//ES"
DOMINIO_UID = "cronogramas-silabos"


def generar_ics(plan: Planificacion, generado: datetime | None = None) -> bytes:
    generado = generado or datetime.now(UTC)
    calendario = Calendar()
    calendario.add("prodid", PRODID)
    calendario.add("version", "2.0")
    calendario.add("calscale", "GREGORIAN")
    calendario.add("method", "PUBLISH")
    calendario.add("x-wr-calname", f"UG {plan.periodo}")

    for evento in plan.eventos:
        vevento = Event()
        vevento.add("uid", _uid(evento.categoria, evento.titulo, evento.rango.inicio.isoformat()))
        vevento.add("dtstamp", generado)
        vevento.add("dtstart", evento.rango.inicio)
        vevento.add("dtend", evento.rango.fin + timedelta(days=1))
        vevento.add("summary", evento.titulo)
        vevento.add("description", evento.descripcion)
        vevento.add("categories", [evento.categoria])
        vevento.add("transp", "TRANSPARENT")
        if evento.recordatorio is not None:
            alarma = Alarm()
            alarma.add("action", "DISPLAY")
            alarma.add("description", evento.titulo)
            alarma.add("trigger", evento.recordatorio)
            vevento.add_component(alarma)
        calendario.add_component(vevento)
    return calendario.to_ical()


def _uid(*partes: str) -> str:
    """UID estable: importar el archivo otra vez actualiza los eventos en lugar de duplicarlos."""
    resumen = hashlib.sha1("|".join(partes).encode("utf-8"), usedforsecurity=False).hexdigest()
    return f"{resumen[:20]}@{DOMINIO_UID}"
