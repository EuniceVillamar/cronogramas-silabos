from datetime import date
from pathlib import Path

import pytest

from extractor.calendario import extraer_calendario
from extractor.evaluacion import evaluar_calendario
from extractor.models import TipoEvento

CALENDARIOS = Path(__file__).parent / "fixtures" / "calendarios"
PRECISION_MINIMA = 0.85


@pytest.fixture(scope="module")
def calendario_ci():
    return extraer_calendario(CALENDARIOS / "ug-ci-2026-2027.pdf")


@pytest.fixture(scope="module")
def calendario_cii():
    return extraer_calendario(CALENDARIOS / "ug-cii-2026-2027.pdf")


@pytest.mark.parametrize("nombre", ["ug-ci-2026-2027", "ug-cii-2026-2027"])
def test_precision_de_fechas_supera_el_objetivo(nombre):
    calendario = extraer_calendario(CALENDARIOS / f"{nombre}.pdf")

    metricas = evaluar_calendario(calendario, CALENDARIOS / f"{nombre}.expected.json")

    assert metricas.precision >= PRECISION_MINIMA
    assert metricas.cobertura >= PRECISION_MINIMA


def test_lee_el_nombre_del_periodo(calendario_ci, calendario_cii):
    assert calendario_ci.nombre == "CI 2026-2027"
    assert calendario_cii.nombre == "CII 2026-2027"


def test_formato_de_varias_tablas_identifica_parciales(calendario_ci):
    examenes = calendario_ci.de_tipo(TipoEvento.EXAMEN)

    assert [(e.parcial, e.rango.inicio, e.rango.fin) for e in examenes] == [
        (1, date(2026, 5, 18), date(2026, 5, 23)),
        (2, date(2026, 7, 13), date(2026, 7, 18)),
    ]


def test_formato_de_una_tabla_continua_la_seccion_en_otra_pagina(calendario_cii):
    feriados = {e.rango.inicio for e in calendario_cii.de_tipo(TipoEvento.FERIADO)}

    assert date(2026, 12, 25) in feriados
    assert date(2027, 2, 8) in feriados


def test_marca_el_anio_equivocado_y_sugiere_el_correcto(calendario_cii):
    advertencias = {e.rango.inicio: e.advertencia for e in calendario_cii.advertencias}

    assert "Probablemente es 09/10/2026" in advertencias[date(2025, 10, 9)]
    assert "no tiene descripción" in advertencias[date(2026, 12, 25)]


def test_omite_notas_y_fechas_de_portada(calendario_ci):
    textos = [e.texto_fecha for e in calendario_ci.eventos]

    assert not any(t.upper().startswith("NOTA") for t in textos)
    assert "01 DE ABRIL DE 2026" not in textos
