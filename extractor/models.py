"""Estructuras que comparten todos los módulos del extractor."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum


class FormatoSilabo(StrEnum):
    TABLA = "tabla"
    LISTA = "lista"
    PARRAFO = "parrafo"
    DESCONOCIDO = "desconocido"


class TipoActividad(StrEnum):
    EXAMEN = "examen"
    ENTREGA = "entrega"
    PROYECTO = "proyecto"
    OTRO = "otro"


class OrigenExtraccion(StrEnum):
    REGLA = "regla"
    IA = "ia"


@dataclass(frozen=True)
class PaginaPDF:
    numero: int
    texto: str
    tablas: tuple[tuple[tuple[str, ...], ...], ...] = ()


@dataclass(frozen=True)
class DocumentoPDF:
    paginas: tuple[PaginaPDF, ...]

    @property
    def texto(self) -> str:
        return "\n".join(pagina.texto for pagina in self.paginas)


@dataclass(frozen=True)
class ActividadExtraida:
    titulo: str
    fecha_texto: str
    origen: OrigenExtraccion
    tipo: TipoActividad = TipoActividad.OTRO
    fecha: date | None = None
    ponderacion: Decimal | None = None
    confianza: float = 0.0
