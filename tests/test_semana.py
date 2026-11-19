from datetime import date
from pathlib import Path

import pytest

from apps.exports.ics import generar_ics
from apps.exports.semana import EventoSemana, leer_eventos, semana_destacada
from extractor.calendario import extraer_calendario
from extractor.planificacion import planificar

CALENDARIO = Path(__file__).parent / "fixtures" / "calendarios" / "ug-cii-2026-2027.pdf"


@pytest.fixture(scope="module")
def eventos():
    plan = planificar(extraer_calendario(CALENDARIO), [])
    return leer_eventos(generar_ics(plan))


def test_lee_titulo_categoria_y_dias_del_ics(eventos):
    examen = next(e for e in eventos if e.titulo == "Exámenes del primer parcial")

    assert (examen.categoria, examen.inicio, examen.fin) == (
        "Examen",
        date(2026, 11, 30),
        date(2026, 12, 5),
    )
    assert examen.icono == "examen"


def test_muestra_la_semana_actual_si_tiene_eventos(eventos):
    semana = semana_destacada(eventos, hoy=date(2026, 12, 2))

    assert semana.lunes == date(2026, 11, 30)
    assert semana.es_actual
    assert [d.nombre for d in semana.dias] == ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
    assert all(
        any(e.titulo == "Exámenes del primer parcial" for e in d.eventos) for d in semana.dias[:6]
    )
    assert not semana.dias[6].eventos


def test_salta_a_la_semana_del_proximo_evento(eventos):
    semana = semana_destacada(eventos, hoy=date(2026, 11, 19))

    assert semana.lunes == date(2026, 11, 30)
    assert not semana.es_actual


def test_usa_la_ultima_semana_cuando_el_periodo_termino():
    eventos = [EventoSemana("Fin del periodo", "Universidad", date(2026, 7, 31), date(2026, 7, 31))]

    semana = semana_destacada(eventos, hoy=date(2026, 11, 19))

    assert semana.lunes == date(2026, 7, 27)
    assert semana.dias[4].eventos


def test_sin_eventos_no_hay_semana():
    assert semana_destacada([], hoy=date(2026, 11, 19)) is None
