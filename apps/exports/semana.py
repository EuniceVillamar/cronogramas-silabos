"""Semana que se muestra en el inicio, a partir del .ics que el estudiante generó."""

from dataclasses import dataclass, field
from datetime import date, timedelta

from icalendar import Calendar

MESES = ("ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC")
DIAS = ("LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM")
ICONOS = {
    "Examen": "examen",
    "Repaso": "repaso",
    "Unidad": "unidad",
    "Evaluación": "evaluacion",
    "Universidad": "universidad",
}


@dataclass(frozen=True)
class EventoSemana:
    titulo: str
    categoria: str
    inicio: date
    fin: date

    @property
    def icono(self) -> str:
        return ICONOS.get(self.categoria, "universidad")


@dataclass
class Dia:
    fecha: date
    eventos: list[EventoSemana] = field(default_factory=list)

    @property
    def mes(self) -> str:
        return MESES[self.fecha.month - 1]

    @property
    def nombre(self) -> str:
        return DIAS[self.fecha.weekday()]


@dataclass
class Semana:
    lunes: date
    dias: list[Dia]
    es_actual: bool


def leer_eventos(contenido: str | bytes) -> list[EventoSemana]:
    eventos = []
    for vevento in Calendar.from_ical(contenido).walk("VEVENT"):
        inicio = vevento.decoded("DTSTART")
        fin = vevento.decoded("DTEND") - timedelta(days=1) if "DTEND" in vevento else inicio
        categorias = vevento.get("CATEGORIES")
        categoria = str(categorias.cats[0]) if categorias and categorias.cats else ""
        eventos.append(EventoSemana(str(vevento["SUMMARY"]), categoria, inicio, fin))
    return sorted(eventos, key=lambda e: (e.inicio, e.titulo))


def semana_destacada(eventos: list[EventoSemana], hoy: date) -> Semana | None:
    """La semana actual si tiene eventos; si no, la del próximo evento; si no, la del último."""
    if not eventos:
        return None
    lunes_actual = hoy - timedelta(days=hoy.weekday())
    domingo_actual = lunes_actual + timedelta(days=6)
    if any(e.inicio <= domingo_actual and e.fin >= lunes_actual for e in eventos):
        referencia = hoy
    else:
        proximos = [e.inicio for e in eventos if e.inicio > hoy]
        referencia = min(proximos) if proximos else eventos[-1].inicio
    lunes = referencia - timedelta(days=referencia.weekday())
    dias = []
    for n in range(7):
        fecha = lunes + timedelta(days=n)
        dias.append(Dia(fecha, [e for e in eventos if e.inicio <= fecha <= e.fin]))
    return Semana(lunes=lunes, dias=dias, es_actual=lunes == lunes_actual)


def semana_de_ejemplo() -> Semana:
    """Semana real del calendario CII 2026-2027, para quien todavía no tiene cuenta."""
    eventos = [
        EventoSemana("Día de difuntos", "Universidad", date(2026, 11, 2), date(2026, 11, 2)),
        EventoSemana(
            "Independencia de Cuenca", "Universidad", date(2026, 11, 3), date(2026, 11, 3)
        ),
        EventoSemana(
            "Gestión de la Configuración: empieza la unidad 2",
            "Unidad",
            date(2026, 11, 4),
            date(2026, 11, 4),
        ),
    ]
    semana = semana_destacada(eventos, hoy=date(2026, 11, 2))
    semana.es_actual = False
    return semana
