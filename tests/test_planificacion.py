from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from icalendar import Calendar

from apps.exports.ics import generar_ics
from extractor.calendario import extraer_calendario
from extractor.models import ComponenteEvaluacion, SilaboExtraido, Tema, Unidad
from extractor.planificacion import Categoria, planificar

CALENDARIOS = Path(__file__).parent / "fixtures" / "calendarios"


@pytest.fixture(scope="module")
def calendario_cii():
    return extraer_calendario(CALENDARIOS / "ug-cii-2026-2027.pdf")


@pytest.fixture
def silabo():
    return SilaboExtraido(
        asignatura="Estructura de Datos",
        codigo="0311313",
        semestre="3",
        horas_docencia=48,
        unidades=(
            Unidad(1, "Introducción", 4, (Tema("1.1", "Concepto de estructuras"),)),
            Unidad(2, "Recursividad", 12, (Tema("2.1", "Algoritmos recursivos"),)),
            Unidad(3, "Listas", 18, (Tema("3.1", "Listas enlazadas"),)),
            Unidad(4, "Árboles", 14, (Tema("4.1", "Árboles binarios"),)),
        ),
        componentes=(
            ComponenteEvaluacion("Acreditación y validación (sumativa)", 34, ("Examen",)),
        ),
    )


def _por_titulo(plan, inicio_del_titulo):
    return [e for e in plan.eventos if e.titulo.startswith(inicio_del_titulo)]


def test_repasos_llevan_los_temas_de_su_parcial(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo], dias_repaso=7)

    primero, segundo = _por_titulo(plan, "Repasar Estructura de Datos")
    assert primero.rango.inicio == date(2026, 11, 23)
    assert "Algoritmos recursivos" in primero.descripcion
    assert "Listas enlazadas" not in primero.descripcion
    assert segundo.rango.inicio == date(2027, 2, 3)
    assert "Listas enlazadas" in segundo.descripcion
    assert primero.recordatorio == timedelta(hours=8)


def test_unidades_se_reparten_segun_sus_horas(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo])

    inicios = [e.rango.inicio for e in plan.eventos if e.categoria == Categoria.UNIDAD]
    assert inicios[0] == date(2026, 10, 12)
    assert inicios == sorted(inicios)
    assert all(e.rango.inicio < date(2027, 2, 10) for e in plan.eventos if e.categoria == "Unidad")


def test_examenes_tienen_recordatorio_y_unidades_por_materia(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo])

    examen = _por_titulo(plan, "Exámenes del primer parcial")[0]
    assert examen.rango.inicio == date(2026, 11, 30)
    assert examen.recordatorio == -timedelta(hours=15)
    assert "Estructura de Datos: U1 Introducción, U2 Recursividad" in examen.descripcion


def test_omite_fechas_fuera_del_periodo_y_eventos_docentes(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo])

    assert [e.rango.inicio for e in plan.omitidos] == [date(2025, 10, 9)]
    titulos = " ".join(e.titulo for e in plan.eventos)
    assert "Heteroevaluación" not in titulos
    assert "calificaciones" not in titulos


def test_funciona_solo_con_el_calendario(calendario_cii):
    plan = planificar(calendario_cii, [])

    assert _por_titulo(plan, "Exámenes del segundo parcial")
    assert not [e for e in plan.eventos if e.categoria == Categoria.REPASO]


def test_ics_es_valido_y_conserva_eventos_y_alarmas(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo])

    contenido = generar_ics(plan, generado=datetime(2026, 11, 19, tzinfo=UTC))
    leido = Calendar.from_ical(contenido)
    eventos = leido.walk("VEVENT")

    assert str(leido["X-WR-CALNAME"]) == "UG CII 2026-2027"
    assert len(eventos) == len(plan.eventos)
    examen = next(e for e in eventos if str(e["SUMMARY"]) == "Exámenes del primer parcial")
    assert examen.decoded("DTSTART") == date(2026, 11, 30)
    assert examen.decoded("DTEND") == date(2026, 12, 6)
    assert examen.walk("VALARM")
    assert len({str(e["UID"]) for e in eventos}) == len(eventos)


def test_ics_mantiene_los_uid_al_generarse_de_nuevo(calendario_cii, silabo):
    plan = planificar(calendario_cii, [silabo])

    primero = Calendar.from_ical(generar_ics(plan)).walk("VEVENT")
    segundo = Calendar.from_ical(generar_ics(plan)).walk("VEVENT")

    assert [str(e["UID"]) for e in primero] == [str(e["UID"]) for e in segundo]
