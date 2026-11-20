"""Extracción de datos del sílabo de la Universidad de Guayaquil.

El sílabo no trae fechas. De él se toman la materia, sus unidades con horas y temas, y los
componentes de evaluación. Ver docs/formatos-silabos.md.
"""

import html
import re
from collections import Counter
from pathlib import Path
from typing import BinaryIO

import pdfplumber

from .models import ComponenteEvaluacion, SilaboExtraido, Tema, Unidad

CONECTORES = {"a", "al", "de", "del", "e", "el", "en", "la", "las", "los", "o", "u", "y", "con"}
FINALES_ESPANOL = set("aeiouáéíóúnsrldzyjx")
SUFIJOS_SUELTOS = {"ción", "sión", "ión", "ón", "ciones", "siones", "iones", "ones", "mente"}
COMPONENTES = (
    "Gestión formativa",
    "Gestión práctica y autónoma",
    "Acreditación y validación (sumativa)",
    "Evaluación diagnóstica",
)
_NUMERO_TEMA = re.compile(r"(?:^|\s)-?\s*(\d+(?:\.\d+)+)\.?(?=\s|[A-ZÁÉÍÓÚÑ¿])")


def extraer_silabo(origen: str | Path | BinaryIO) -> SilaboExtraido:
    with pdfplumber.open(origen) as pdf:
        paginas = list(pdf.pages)
        texto = "\n".join(pagina.extract_text() or "" for pagina in paginas)
        tablas = [tabla for pagina in paginas for tabla in pagina.extract_tables()]
        vocabulario = _vocabulario(texto)
        asignatura, codigo, semestre, horas_docencia = _datos_informativos(tablas, vocabulario)
        temas = _temas_por_unidad(paginas, vocabulario)
        unidades = tuple(
            Unidad(numero, nombre, horas, tuple(temas.get(numero, ())))
            for numero, nombre, horas in _unidades(tablas, vocabulario)
        )
        componentes = _componentes(tablas, vocabulario)

    return SilaboExtraido(
        asignatura=asignatura,
        codigo=codigo,
        semestre=semestre,
        unidades=unidades,
        componentes=componentes,
        horas_docencia=horas_docencia,
        advertencias=tuple(_advertencias(unidades, componentes, horas_docencia)),
    )


# --- Palabras partidas al final de una línea ------------------------------------------------


def _vocabulario(texto: str) -> Counter:
    return Counter(re.findall(r"[^\W\d_]+", texto.lower()))


def unir_lineas(lineas: list[str], vocabulario: Counter) -> str:
    """Une las líneas de una celda, sin espacio cuando una palabra quedó partida en dos.

    En columnas angostas el PDF corta palabras sin guion: "Responsabilid" / "ad".
    """
    texto = ""
    for linea in (linea.strip() for linea in lineas):
        if not linea:
            continue
        if texto and _es_continuacion(texto, linea, vocabulario):
            texto += linea
        else:
            texto = f"{texto} {linea}" if texto else linea
    return re.sub(r"\s+", " ", texto).strip()


def _es_continuacion(anterior: str, siguiente: str, vocabulario: Counter) -> bool:
    previa = re.search(r"([^\W\d_]+)$", anterior)
    fragmento = re.match(r"([^\W\d_]+)", siguiente)
    if not previa or not fragmento:
        return False
    previa, fragmento = previa.group(1), fragmento.group(1)
    if previa[-1].islower() != fragmento[0].islower():
        return False
    unida = (previa + fragmento).lower()
    if vocabulario[unida] > 0 or fragmento.lower() in SUFIJOS_SUELTOS:
        return True
    if previa[-1].lower() not in FINALES_ESPANOL:
        return True
    return previa.lower().endswith(("ció", "sió")) and fragmento.lower().startswith("n")


def _titulo(texto: str) -> str:
    """Pasa un título en mayúsculas a tipo oración, conservando siglas como "(TDA)"."""
    resultado = []
    for i, palabra in enumerate(texto.split()):
        if re.fullmatch(r"\([A-ZÁÉÍÓÚÑ]{2,4}\)", palabra):
            resultado.append(palabra)
            continue
        minuscula = palabra.lower()
        es_conector = i and minuscula in CONECTORES
        resultado.append(minuscula if es_conector else minuscula[:1].upper() + minuscula[1:])
    return " ".join(resultado)


def _celda(celda: str | None, vocabulario: Counter) -> str:
    return unir_lineas((celda or "").split("\n"), vocabulario)


# --- Sección A: datos informativos ----------------------------------------------------------


def _datos_informativos(tablas, vocabulario) -> tuple[str, str, str, int | None]:
    asignatura = codigo = semestre = ""
    horas_docencia = None
    for tabla in tablas:
        for fila in tabla:
            celdas = [_celda(c, vocabulario) for c in fila]
            for i, celda in enumerate(celdas):
                siguiente = next((c for c in celdas[i + 1 :] if c), "")
                if celda == "Asignatura:" and not asignatura:
                    asignatura = _titulo(siguiente)
                elif celda == "Código:" and not codigo:
                    codigo = siguiente
                elif celda == "Semestre:" and not semestre:
                    semestre = siguiente
                elif "docencia" in celda.lower() and horas_docencia is None:
                    horas_docencia = _entero(siguiente)
    return asignatura, codigo, semestre, horas_docencia


def _entero(texto: str) -> int | None:
    coincidencia = re.search(r"\d+(?:[.,]\d+)?", texto or "")
    return round(float(coincidencia.group().replace(",", "."))) if coincidencia else None


# --- Sección D: unidades y temas ------------------------------------------------------------


def _unidades(tablas, vocabulario) -> list[tuple[int, str, int]]:
    unidades = {}
    for tabla in tablas:
        for fila in tabla:
            celdas = [_celda(c, vocabulario) for c in fila]
            if len(celdas) < 7 or celdas[0] != "Unidad #:":
                continue
            numero = _entero(celdas[1])
            if numero is None or numero in unidades:
                continue
            horas = next(
                (_entero(c) for c in celdas[5:] if _entero(c) is not None),
                0,
            )
            unidades[numero] = (numero, _titulo(celdas[3]), horas)
    return [unidades[n] for n in sorted(unidades)]


def _temas_por_unidad(paginas, vocabulario) -> dict[int, list[Tema]]:
    texto = unir_lineas(_columna_contenidos(paginas), vocabulario)
    texto = html.unescape(texto)
    partes = _NUMERO_TEMA.split(texto)
    temas: dict[int, list[Tema]] = {}
    vistos = set()
    for numero, titulo in zip(partes[1::2], partes[2::2], strict=False):
        titulo = re.sub(r"\s+", " ", titulo).strip(" -.;:")
        if not titulo or numero in vistos:
            continue
        vistos.add(numero)
        temas.setdefault(int(numero.split(".")[0]), []).append(Tema(numero, titulo))
    return temas


def _columna_contenidos(paginas) -> list[str]:
    """Recorta la columna "Contenidos a desarrollar", que las tablas extraídas pierden."""
    lineas: list[str] = []
    columna = None
    en_unidades = False
    for pagina in paginas:
        palabras = pagina.extract_words()
        textos = {p["text"] for p in palabras}
        if "UNIDADES" in textos:
            en_unidades = True
        if not en_unidades:
            continue
        encabezado = next((p for p in palabras if p["text"] == "Contenidos"), None)
        if encabezado:
            derecha = [
                p["x0"]
                for p in palabras
                if p["text"] == "Aprendizaje" and p["x0"] > encabezado["x0"]
            ]
            if derecha:
                columna = (encabezado["x0"] - 2, min(derecha) - 2)
            marcas = [p["bottom"] for p in palabras if p["text"] in ("(ACD)", "(APE).", "(AA).")]
            arriba = max(marcas, default=encabezado["bottom"]) + 2
        else:
            titulo = next((p for p in palabras if p["text"] == "SÍLABO"), None)
            arriba = titulo["bottom"] + 2 if titulo else 0
        if columna is None:
            continue
        fin = [p["top"] for p in palabras if p["text"] in ("E:", "EVALUACIÓN")]
        abajo = min(fin) - 2 if fin else pagina.height - 40
        if abajo > arriba:
            recorte = pagina.crop((columna[0], arriba, columna[1], abajo))
            lineas.extend((recorte.extract_text() or "").split("\n"))
        if fin:
            break
    return lineas


# --- Sección E: evaluación ------------------------------------------------------------------


def _componentes(tablas, vocabulario) -> tuple[ComponenteEvaluacion, ...]:
    pesos: dict[str, int] = {}
    actividades: dict[str, list[str]] = {}
    actual = None
    for tabla in tablas:
        for fila in tabla:
            celdas = [_celda(c, vocabulario) for c in fila]
            if not celdas:
                continue
            nombre = next((c for c in COMPONENTES if celdas[0].startswith(c)), None)
            if nombre:
                actual = nombre
                peso = _entero(celdas[1]) if len(celdas) > 1 else None
                if peso is not None:
                    pesos[nombre] = peso
            if actual and celdas[-1] == "X" and len(celdas) >= 3:
                actividad = re.sub(r"^Otros:\s*Detallar\.?\s*", "", celdas[2]).strip(" .")
                if actividad:
                    actividades.setdefault(actual, []).append(actividad)
    return tuple(
        ComponenteEvaluacion(nombre, pesos[nombre], tuple(actividades.get(nombre, ())))
        for nombre in COMPONENTES
        if nombre in pesos
    )


def _advertencias(unidades, componentes, horas_docencia) -> list[str]:
    avisos = []
    if not unidades:
        avisos.append("No se encontraron unidades temáticas.")
    horas = sum(u.horas_acd for u in unidades)
    if unidades and horas_docencia and horas != horas_docencia:
        avisos.append(
            f"Las horas ACD de las unidades suman {horas} y la sección A indica {horas_docencia}."
        )
    for unidad in unidades:
        if not unidad.temas:
            avisos.append(f"No se encontraron temas de la unidad {unidad.numero}.")
    total = sum(c.ponderacion for c in componentes)
    if componentes and total != 100:
        avisos.append(f"Las ponderaciones suman {total} en lugar de 100.")
    return avisos
