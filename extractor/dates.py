"""Interpretación de fechas escritas en español, como las del calendario académico."""

import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta

MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
DIAS_SEMANA = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")

_MES = "|".join(MESES)
_FECHA = re.compile(
    rf"""^
    (?:(?:del\s+)?(?P<d1>\d{{1,2}})(?:\s+de\s+(?P<m1>{_MES}))?(?:\s+de\s+(?P<y1>\d{{4}}))?
       \s+(?P<sep>al|y)\s+)?
    (?P<d2>\d{{1,2}})\s+de\s+(?P<m2>{_MES})\s+de\s+(?P<y2>\d{{4}})
    $""",
    re.VERBOSE,
)


@dataclass(frozen=True)
class RangoFechas:
    """Rango de días, ambos incluidos. Una fecha única tiene inicio igual a fin."""

    inicio: date
    fin: date

    @property
    def dias(self) -> int:
        return (self.fin - self.inicio).days + 1

    def contiene(self, dia: date) -> bool:
        return self.inicio <= dia <= self.fin

    def fechas(self) -> list[date]:
        return [self.inicio + timedelta(days=n) for n in range(self.dias)]


def sin_tildes(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def _normalizar(texto: str) -> str:
    texto = sin_tildes(texto).lower()
    texto = re.sub(r"\(.*?\)", " ", texto)
    texto = texto.replace("/", " ")
    texto = re.sub(rf"\b(?:{'|'.join(DIAS_SEMANA)})\b", " ", texto)
    texto = re.sub(r"\s+de+l\s+(\d{4})\b", r" de \1", texto)
    return re.sub(r"\s+", " ", texto).strip(" .,")


def interpretar_rango(texto: str) -> RangoFechas | None:
    """Convierte "Del 18 al 23 de mayo de 2026" y variantes en un rango; None si no es una fecha.

    Acepta días de la semana, "del" antes del año, rangos que cruzan de mes o de año,
    días unidos por "y" y anotaciones entre paréntesis.
    """
    coincidencia = _FECHA.match(_normalizar(texto))
    if not coincidencia:
        return None
    partes = coincidencia.groupdict()
    fin = _crear_fecha(int(partes["y2"]), MESES[partes["m2"]], int(partes["d2"]))
    if fin is None:
        return None
    if partes["d1"] is None:
        return RangoFechas(fin, fin)

    mes_inicio = MESES[partes["m1"]] if partes["m1"] else fin.month
    if partes["y1"]:
        anio_inicio = int(partes["y1"])
    else:
        anio_inicio = fin.year - 1 if mes_inicio > fin.month else fin.year
    inicio = _crear_fecha(anio_inicio, mes_inicio, int(partes["d1"]))
    if inicio is None or inicio > fin:
        return None
    return RangoFechas(inicio, fin)


def _crear_fecha(anio: int, mes: int, dia: int) -> date | None:
    try:
        return date(anio, mes, dia)
    except ValueError:
        return None
