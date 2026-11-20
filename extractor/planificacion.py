"""Combina el calendario académico con los sílabos para armar el calendario del estudiante.

Las fechas salen del calendario. El sílabo aporta los temas: cada unidad se ubica en el
tiempo repartiendo los días de clase de cada parcial en proporción a sus horas ACD.
"""

import re
from dataclasses import dataclass, field
from datetime import date, timedelta

from .calendario import SIN_DESCRIPCION
from .dates import RangoFechas
from .models import (
    TIPOS_PARA_ESTUDIANTES,
    CalendarioAcademico,
    EventoAcademico,
    SilaboExtraido,
    TipoEvento,
    Unidad,
)

DIAS_DE_REPASO = 7
ORDINALES = {1: "primer", 2: "segundo", 3: "tercer", 4: "cuarto"}
AVISO_ESTIMADO = "Fecha estimada según las horas del sílabo. Confírmala con tu docente."

# Recordatorios relativos al inicio de un evento de día completo (00:00).
A_LAS_8 = timedelta(hours=8)
DIA_ANTERIOR_A_LAS_9 = -timedelta(hours=15)


class Categoria:
    UNIVERSIDAD = "Universidad"
    EXAMEN = "Examen"
    REPASO = "Repaso"
    UNIDAD = "Unidad"
    EVALUACION = "Evaluación"


@dataclass(frozen=True)
class EventoCalendario:
    titulo: str
    rango: RangoFechas
    descripcion: str
    categoria: str
    recordatorio: timedelta | None = None


@dataclass(frozen=True)
class Parcial:
    numero: int
    clases: RangoFechas
    examenes: RangoFechas

    @property
    def nombre(self) -> str:
        return f"{ORDINALES.get(self.numero, f'{self.numero}.º')} parcial"


@dataclass
class Planificacion:
    periodo: str
    eventos: list[EventoCalendario] = field(default_factory=list)
    omitidos: list[EventoAcademico] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)


def planificar(
    calendario: CalendarioAcademico,
    silabos: list[SilaboExtraido],
    dias_repaso: int = DIAS_DE_REPASO,
) -> Planificacion:
    plan = Planificacion(periodo=calendario.nombre)
    parciales = _parciales(calendario)
    if not parciales:
        plan.advertencias.append(
            "No encontré el inicio de clases y los exámenes de cada parcial en el calendario."
        )
    temas_por_parcial = {silabo.codigo or silabo.asignatura: {} for silabo in silabos}

    for silabo in silabos:
        clave = silabo.codigo or silabo.asignatura
        for aviso in silabo.advertencias:
            plan.advertencias.append(f"{silabo.asignatura}: {aviso}")
        if not parciales:
            continue
        ubicacion = _ubicar_unidades(silabo.unidades, parciales)
        temas_por_parcial[clave] = {
            p.numero: [u for u, (_, parcial) in ubicacion.items() if parcial == p.numero]
            for p in parciales
        }
        plan.eventos.append(_plan_de_evaluacion(silabo, parciales[0]))
        for unidad, (inicio, _) in ubicacion.items():
            plan.eventos.append(_inicio_de_unidad(silabo, unidad, inicio))
        for parcial in parciales:
            unidades = temas_por_parcial[clave][parcial.numero]
            plan.eventos.append(_repaso(silabo, parcial, unidades, dias_repaso))

    for evento in calendario.eventos:
        if evento.tipo not in TIPOS_PARA_ESTUDIANTES:
            continue
        if evento.advertencia and "fuera del periodo" in evento.advertencia:
            plan.omitidos.append(evento)
            continue
        plan.eventos.append(_evento_institucional(evento, plan.periodo, silabos, temas_por_parcial))

    plan.eventos.sort(key=lambda e: (e.rango.inicio, e.categoria, e.titulo))
    return plan


def _parciales(calendario: CalendarioAcademico) -> list[Parcial]:
    inicios = {e.parcial: e.rango.inicio for e in calendario.de_tipo(TipoEvento.INICIO_CLASES)}
    parciales = []
    for examen in calendario.de_tipo(TipoEvento.EXAMEN):
        inicio = inicios.get(examen.parcial)
        if examen.parcial is None or inicio is None or inicio >= examen.rango.inicio:
            continue
        clases = RangoFechas(inicio, examen.rango.inicio - timedelta(days=1))
        parciales.append(Parcial(examen.parcial, clases, examen.rango))
    return sorted(parciales, key=lambda p: p.numero)


def _ubicar_unidades(
    unidades: tuple[Unidad, ...], parciales: list[Parcial]
) -> dict[Unidad, tuple[date, int]]:
    """Devuelve la fecha estimada de inicio de cada unidad y el parcial en el que se evalúa."""
    total_horas = sum(u.horas_acd for u in unidades)
    total_dias = sum(p.clases.dias for p in parciales)
    if not total_horas or not total_dias:
        return {}
    ubicacion = {}
    acumuladas = 0
    for unidad in unidades:
        inicio = _dia_de_clase(acumuladas / total_horas * total_dias, parciales)
        mitad = (acumuladas + unidad.horas_acd / 2) / total_horas * total_dias
        ubicacion[unidad] = (inicio[0], _dia_de_clase(mitad, parciales)[1])
        acumuladas += unidad.horas_acd
    return ubicacion


def _dia_de_clase(desplazamiento: float, parciales: list[Parcial]) -> tuple[date, int]:
    restante = int(desplazamiento)
    for parcial in parciales:
        if restante < parcial.clases.dias:
            return parcial.clases.inicio + timedelta(days=restante), parcial.numero
        restante -= parcial.clases.dias
    ultimo = parciales[-1]
    return ultimo.clases.fin, ultimo.numero


def temas_para_mostrar(unidad: Unidad, limite: int = 8) -> list[str]:
    """Temas principales (1.1, 1.2, …); si la unidad tiene uno solo, sus subtemas."""
    principales = [t for t in unidad.temas if t.numero.count(".") == 1]
    if len(principales) <= 1:
        subtemas = [t for t in unidad.temas if t.numero.count(".") == 2]
        principales = subtemas or principales
    return [f"{t.numero} {t.titulo}" for t in principales[:limite]]


def _lista_de_temas(unidades: list[Unidad]) -> str:
    bloques = []
    for unidad in unidades:
        lineas = [f"Unidad {unidad.numero}: {unidad.nombre}"]
        lineas += [f"• {tema}" for tema in temas_para_mostrar(unidad)]
        bloques.append("\n".join(lineas))
    return "\n\n".join(bloques)


def _sumativo(silabo: SilaboExtraido) -> str:
    for componente in silabo.componentes:
        if "sumativa" in componente.nombre.lower():
            actividades = "; ".join(componente.actividades) or "sin detalle"
            return f"Evaluación sumativa: {componente.ponderacion} % ({actividades})."
    return ""


def _plan_de_evaluacion(silabo: SilaboExtraido, primero: Parcial) -> EventoCalendario:
    lineas = [f"{silabo.asignatura} ({silabo.codigo}), semestre {silabo.semestre}.", ""]
    for componente in silabo.componentes:
        lineas.append(f"{componente.nombre}: {componente.ponderacion} %")
        lineas += [f"• {actividad}" for actividad in componente.actividades]
    return EventoCalendario(
        titulo=f"{silabo.asignatura}: plan de evaluación",
        rango=RangoFechas(primero.clases.inicio, primero.clases.inicio),
        descripcion="\n".join(lineas).strip(),
        categoria=Categoria.EVALUACION,
    )


def _inicio_de_unidad(silabo: SilaboExtraido, unidad: Unidad, inicio: date) -> EventoCalendario:
    temas = "\n".join(f"• {tema}" for tema in temas_para_mostrar(unidad))
    descripcion = (
        f"Unidad {unidad.numero}: {unidad.nombre}\n"
        f"Horas de docencia: {unidad.horas_acd} de {silabo.horas_acd}.\n\n"
        f"Temas:\n{temas}\n\n{AVISO_ESTIMADO}"
    )
    return EventoCalendario(
        titulo=f"{silabo.asignatura}: empieza la unidad {unidad.numero}",
        rango=RangoFechas(inicio, inicio),
        descripcion=descripcion,
        categoria=Categoria.UNIDAD,
    )


def _repaso(
    silabo: SilaboExtraido, parcial: Parcial, unidades: list[Unidad], dias_repaso: int
) -> EventoCalendario:
    dia = max(parcial.examenes.inicio - timedelta(days=dias_repaso), parcial.clases.inicio)
    if unidades:
        temas = f"Temas a repasar:\n\n{_lista_de_temas(unidades)}"
    else:
        temas = "Según las horas del sílabo, ninguna unidad termina en este parcial."
    descripcion = "\n\n".join(
        parte
        for parte in (
            f"Los exámenes del {parcial.nombre} empiezan el {parcial.examenes.inicio:%d/%m/%Y}.",
            temas,
            _sumativo(silabo),
            AVISO_ESTIMADO,
        )
        if parte
    )
    return EventoCalendario(
        titulo=f"Repasar {silabo.asignatura} para el {parcial.nombre}",
        rango=RangoFechas(dia, dia),
        descripcion=descripcion,
        categoria=Categoria.REPASO,
        recordatorio=A_LAS_8,
    )


def _evento_institucional(
    evento: EventoAcademico,
    periodo: str,
    silabos: list[SilaboExtraido],
    temas_por_parcial: dict[str, dict[int, list[Unidad]]],
) -> EventoCalendario:
    titulo = _titulo_institucional(evento)
    partes = [evento.descripcion, f"Fuente: calendario académico {periodo}."]
    if evento.advertencia:
        partes.append(f"Revisar: {evento.advertencia}")
    categoria = Categoria.UNIVERSIDAD
    recordatorio = None
    if evento.tipo in (TipoEvento.EXAMEN, TipoEvento.RECUPERACION):
        categoria = Categoria.EXAMEN
        recordatorio = DIA_ANTERIOR_A_LAS_9
        if evento.tipo == TipoEvento.EXAMEN and silabos:
            partes.insert(1, _temas_del_examen(evento.parcial, silabos, temas_por_parcial))
    elif evento.tipo in (TipoEvento.MATRICULA, TipoEvento.RETIRO):
        recordatorio = A_LAS_8
    return EventoCalendario(
        titulo=titulo,
        rango=evento.rango,
        descripcion="\n\n".join(partes),
        categoria=categoria,
        recordatorio=recordatorio,
    )


def _temas_del_examen(parcial, silabos, temas_por_parcial) -> str:
    lineas = ["Unidades por materia:"]
    for silabo in silabos:
        unidades = temas_por_parcial.get(silabo.codigo or silabo.asignatura, {}).get(parcial, [])
        nombres = ", ".join(f"U{u.numero} {u.nombre}" for u in unidades) or "sin unidades"
        lineas.append(f"• {silabo.asignatura}: {nombres}")
    return "\n".join(lineas)


def _titulo_institucional(evento: EventoAcademico) -> str:
    ordinal = ORDINALES.get(evento.parcial or 0, "")
    if evento.tipo == TipoEvento.INICIO_CLASES:
        return f"Inicio de clases del {ordinal} parcial".replace("del  ", "del ")
    if evento.tipo == TipoEvento.EXAMEN:
        return f"Exámenes del {ordinal} parcial".replace("del  ", "del ")
    if evento.tipo == TipoEvento.RECUPERACION:
        return "Exámenes de recuperación y mejoramiento"
    if evento.tipo == TipoEvento.FIN_PERIODO:
        return "Fin del periodo académico"
    if evento.descripcion == SIN_DESCRIPCION:
        return "Feriado"
    titulo = re.sub(r"\s*\(.*?\)\s*", " ", evento.descripcion).strip(" .")
    if evento.tipo == TipoEvento.TRAMITE:
        return f"Cambio de carrera: {titulo[:1].lower()}{titulo[1:]}"
    return titulo
