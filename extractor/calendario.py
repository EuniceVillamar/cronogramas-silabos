"""Extracción de eventos del calendario académico de la Universidad de Guayaquil.

El calendario es una tabla de dos columnas: fecha y actividad. Los títulos de sección
(MATRICULACIÓN, VACACIONES Y FERIADOS, …) ocupan filas sin actividad, y las notas empiezan
con "NOTA". Una misma sección puede continuar en la página siguiente.
"""

import re
from datetime import date, timedelta
from pathlib import Path
from typing import BinaryIO

from .dates import DIAS_SEMANA, RangoFechas, interpretar_rango, sin_tildes
from .models import CalendarioAcademico, DocumentoPDF, EventoAcademico, TipoEvento
from .reader import leer_pdf

MARGEN_ANTES_DE_CLASES = timedelta(days=120)
MARGEN_DESPUES_DEL_FIN = timedelta(days=30)
SIN_DESCRIPCION = "Sin descripción en el calendario"


def extraer_calendario(origen: str | Path | BinaryIO | DocumentoPDF) -> CalendarioAcademico:
    documento = origen if isinstance(origen, DocumentoPDF) else leer_pdf(origen)
    eventos = list(_leer_filas(documento))
    return CalendarioAcademico(
        nombre=_nombre_periodo(documento.texto),
        eventos=tuple(_validar(eventos)),
    )


def _leer_filas(documento: DocumentoPDF):
    seccion = ""
    for pagina in documento.paginas:
        for tabla in pagina.tablas:
            for fila in tabla:
                celdas = [_limpiar(celda) for celda in fila]
                texto_fecha = celdas[0] if celdas else ""
                descripcion = " ".join(celda for celda in celdas[1:] if celda)
                if not texto_fecha or texto_fecha.upper().startswith("NOTA"):
                    continue
                rango = interpretar_rango(texto_fecha)
                if rango is None:
                    if not descripcion and _es_titulo(texto_fecha):
                        seccion = texto_fecha
                    continue
                if not descripcion and texto_fecha.isupper():
                    continue  # Fecha de portada, como "01 DE ABRIL DE 2026".
                tipo, parcial = _clasificar(seccion, descripcion)
                yield EventoAcademico(
                    rango=rango,
                    descripcion=descripcion or SIN_DESCRIPCION,
                    seccion=seccion,
                    tipo=tipo,
                    texto_fecha=texto_fecha,
                    parcial=parcial,
                    advertencia=None if descripcion else "La fila no tiene descripción.",
                )


def _limpiar(celda: str | None) -> str:
    return re.sub(r"\s+", " ", celda or "").strip()


def _es_titulo(texto: str) -> bool:
    return texto.isupper() and not re.search(r"\d", texto)


def _clasificar(seccion: str, descripcion: str) -> tuple[TipoEvento, int | None]:
    texto = sin_tildes(descripcion).lower()
    seccion = sin_tildes(seccion).lower()
    parcial = re.search(r"(\d)\s*(?:er|do|ro|to)?\.?\s*parcial", texto)
    numero = int(parcial.group(1)) if parcial else None

    if "feriado" in texto or (not texto and "feriado" in seccion):
        return TipoEvento.FERIADO, None
    if "vacaciones" in texto:
        return TipoEvento.VACACIONES, None
    if "inicio de clases" in texto:
        return TipoEvento.INICIO_CLASES, numero
    if "calificaciones" in texto or "actas" in texto:
        if "fin del periodo" in texto:
            return TipoEvento.FIN_PERIODO, None
        return TipoEvento.CALIFICACIONES, numero
    if "recuperacion" in texto:
        return TipoEvento.RECUPERACION, None
    if "examenes" in texto:
        return TipoEvento.EXAMEN, numero
    if "matricula" in texto:
        return TipoEvento.MATRICULA, None
    if "retiro" in texto:
        return TipoEvento.RETIRO, None
    if "cambio de carrera" in seccion:
        return TipoEvento.TRAMITE, None
    if "docente" in seccion:
        return TipoEvento.DOCENTE, None
    return TipoEvento.ADMINISTRATIVO, None


def _validar(eventos: list[EventoAcademico]) -> list[EventoAcademico]:
    inicios = [e.rango.inicio for e in eventos if e.tipo == TipoEvento.INICIO_CLASES]
    finales = [e.rango.fin for e in eventos if e.tipo == TipoEvento.FIN_PERIODO]
    ventana = None
    if inicios and finales:
        ventana = RangoFechas(
            min(inicios) - MARGEN_ANTES_DE_CLASES, max(finales) + MARGEN_DESPUES_DEL_FIN
        )
    return [_revisar(evento, ventana) for evento in eventos]


def _revisar(evento: EventoAcademico, ventana: RangoFechas | None) -> EventoAcademico:
    problemas = [evento.advertencia] if evento.advertencia else []
    dias_ok = _dias_de_semana_coinciden(evento.texto_fecha, evento.rango)
    fuera = ventana is not None and not (
        ventana.contiene(evento.rango.inicio) and ventana.contiene(evento.rango.fin)
    )
    if fuera:
        problemas.append("La fecha está fuera del periodo académico.")
    if not dias_ok:
        problemas.append("El día de la semana no coincide con la fecha.")
    if fuera or not dias_ok:
        sugerida = _sugerir_anio(evento, ventana)
        if sugerida:
            problemas.append(f"Probablemente es {sugerida:%d/%m/%Y}.")
    if not problemas:
        return evento
    return EventoAcademico(**{**evento.__dict__, "advertencia": " ".join(problemas)})


def _dias_mencionados(texto: str) -> list[int]:
    palabras = re.findall(r"[a-z]+", sin_tildes(texto).lower())
    return [DIAS_SEMANA.index(p) for p in palabras if p in DIAS_SEMANA]


def _dias_de_semana_coinciden(texto: str, rango: RangoFechas) -> bool:
    dias = _dias_mencionados(texto)
    esperados = [rango.inicio.weekday(), rango.fin.weekday()]
    return all(dia == esperado for dia, esperado in zip(dias, esperados, strict=False))


def _sugerir_anio(evento: EventoAcademico, ventana: RangoFechas | None) -> date | None:
    """Busca el mismo día y mes en un año vecino que caiga en el periodo y en el día indicado."""
    if ventana is None or evento.rango.dias != 1:
        return None
    dias = _dias_mencionados(evento.texto_fecha)
    original = evento.rango.inicio
    for anio in (original.year + 1, original.year - 1):
        try:
            candidata = original.replace(year=anio)
        except ValueError:
            continue
        if ventana.contiene(candidata) and (not dias or dias[0] == candidata.weekday()):
            return candidata
    return None


def _nombre_periodo(texto: str) -> str:
    coincidencia = re.search(r"\b(C[I]+)\s+(\d{4})\s*-\s*(\d{4})", texto)
    if coincidencia:
        return f"{coincidencia.group(1)} {coincidencia.group(2)}-{coincidencia.group(3)}"
    return "Calendario académico"
