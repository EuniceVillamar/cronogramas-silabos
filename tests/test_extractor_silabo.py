import os
from collections import Counter
from pathlib import Path

import pytest

from extractor.silabo import _titulo, extraer_silabo, unir_lineas

# Los sílabos reales tienen nombres de docentes y no se suben al repositorio.
# Estas pruebas corren solo donde existe la carpeta local con los PDF.
SILABOS = Path(os.environ.get("SILABOS_DIR", Path(__file__).parents[1] / "formato"))
requiere_silabos = pytest.mark.skipif(
    not (SILABOS / "silabo2.pdf").exists(), reason="Sílabos reales no disponibles."
)


@pytest.mark.parametrize(
    ("lineas", "esperado"),
    [
        (["Responsabilid", "ad ética"], "Responsabilidad ética"),
        (["Requerimient", "os, análisis"], "Requerimientos, análisis"),
        (["Implementaci", "ón del software"], "Implementación del software"),
        (["INTRODUCCIÓ", "N A LA"], "INTRODUCCIÓN A LA"),
        (["La crisis", "del software"], "La crisis del software"),
        (["Necesidad de", "las estructuras"], "Necesidad de las estructuras"),
    ],
)
def test_une_palabras_partidas_sin_unir_palabras_completas(lineas, esperado):
    vocabulario = Counter(["responsabilidad", "introducción", "crisis", "de", "las"])

    assert unir_lineas(lineas, vocabulario) == esperado


def test_titulo_pasa_mayusculas_a_oracion_y_conserva_siglas():
    assert (
        _titulo("INTRODUCCIÓN A LAS ESTRUCTURAS DE DATOS (TDA) CON OBJETOS")
        == "Introducción a las Estructuras de Datos (TDA) con Objetos"
    )


@requiere_silabos
def test_extrae_materia_unidades_y_temas():
    silabo = extraer_silabo(SILABOS / "silabo2.pdf")

    assert (silabo.asignatura, silabo.codigo, silabo.semestre) == (
        "Estructura de Datos",
        "0311313",
        "3",
    )
    assert [u.horas_acd for u in silabo.unidades] == [4, 12, 18, 14]
    assert silabo.horas_acd == silabo.horas_docencia == 48
    primeros = [t.titulo for t in silabo.unidades[1].temas if t.numero.count(".") == 1]
    assert primeros == [
        "Algoritmos recursivos",
        "Algoritmos de ordenamiento de datos",
        "Algoritmos de búsqueda de datos",
    ]
    assert silabo.advertencias == ()


@requiere_silabos
@pytest.mark.parametrize("archivo", ["sillabo1.pdf", "silabo2.pdf", "silabo3.pdf", "silabo4.pdf"])
def test_componentes_suman_cien_y_cada_unidad_tiene_temas(archivo):
    silabo = extraer_silabo(SILABOS / archivo)

    assert sum(c.ponderacion for c in silabo.componentes) == 100
    assert all(unidad.temas for unidad in silabo.unidades)
