"""Estructuras que comparten todos los módulos del extractor."""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum

from .dates import RangoFechas


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


class TipoEvento(StrEnum):
    """Clasificación de una fila del calendario académico."""

    INICIO_CLASES = "inicio_clases"
    EXAMEN = "examen"
    RECUPERACION = "recuperacion"
    FIN_PERIODO = "fin_periodo"
    FERIADO = "feriado"
    VACACIONES = "vacaciones"
    MATRICULA = "matricula"
    RETIRO = "retiro"
    TRAMITE = "tramite"
    CALIFICACIONES = "calificaciones"
    DOCENTE = "docente"
    ADMINISTRATIVO = "administrativo"


TIPOS_PARA_ESTUDIANTES = frozenset(
    {
        TipoEvento.INICIO_CLASES,
        TipoEvento.EXAMEN,
        TipoEvento.RECUPERACION,
        TipoEvento.FIN_PERIODO,
        TipoEvento.FERIADO,
        TipoEvento.VACACIONES,
        TipoEvento.MATRICULA,
        TipoEvento.RETIRO,
        TipoEvento.TRAMITE,
    }
)


@dataclass(frozen=True)
class EventoAcademico:
    rango: RangoFechas
    descripcion: str
    seccion: str
    tipo: TipoEvento
    texto_fecha: str
    parcial: int | None = None
    advertencia: str | None = None


@dataclass(frozen=True)
class CalendarioAcademico:
    nombre: str
    eventos: tuple[EventoAcademico, ...]

    def de_tipo(self, tipo: TipoEvento) -> list[EventoAcademico]:
        return [evento for evento in self.eventos if evento.tipo == tipo]

    @property
    def advertencias(self) -> list[EventoAcademico]:
        return [evento for evento in self.eventos if evento.advertencia]


@dataclass(frozen=True)
class Tema:
    numero: str
    titulo: str


@dataclass(frozen=True)
class Unidad:
    numero: int
    nombre: str
    horas_acd: int
    temas: tuple[Tema, ...] = ()


@dataclass(frozen=True)
class ComponenteEvaluacion:
    nombre: str
    ponderacion: int
    actividades: tuple[str, ...] = ()


@dataclass(frozen=True)
class SilaboExtraido:
    asignatura: str
    codigo: str
    semestre: str
    unidades: tuple[Unidad, ...]
    componentes: tuple[ComponenteEvaluacion, ...] = ()
    horas_docencia: int | None = None
    advertencias: tuple[str, ...] = field(default=())

    @property
    def horas_acd(self) -> int:
        return sum(unidad.horas_acd for unidad in self.unidades)
