from datetime import date

import pytest

from extractor.dates import RangoFechas, interpretar_rango


@pytest.mark.parametrize(
    ("texto", "inicio", "fin"),
    [
        ("01 de abril de 2026", date(2026, 4, 1), date(2026, 4, 1)),
        ("26 de mayo del 2026", date(2026, 5, 26), date(2026, 5, 26)),
        ("Viernes 03 de abril del 2026", date(2026, 4, 3), date(2026, 4, 3)),
        ("Del 18 al 23 de mayo de 2026", date(2026, 5, 18), date(2026, 5, 23)),
        (
            "Del 30 de noviembre al 05 de diciembre de 2026",
            date(2026, 11, 30),
            date(2026, 12, 5),
        ),
        (
            "Del 01 de septiembre de 2026 al 25 de febrero de 2027\n(Durante todo el ciclo)",
            date(2026, 9, 1),
            date(2027, 2, 25),
        ),
        ("Lunes 16 al martes 17 de febrero de 2026", date(2026, 2, 16), date(2026, 2, 17)),
        (
            "Jueves 26 de febrero al jueves 19 de marzo de 2026",
            date(2026, 2, 26),
            date(2026, 3, 19),
        ),
        (
            "Del Miercoles 23 de septiembre al 04 de octubre de 2026",
            date(2026, 9, 23),
            date(2026, 10, 4),
        ),
        (
            "Del miercoles 23 al jueves 31 de diciembre de 2026",
            date(2026, 12, 23),
            date(2026, 12, 31),
        ),
        ("Lunes 08 y martes 09 de febrero de 2027", date(2027, 2, 8), date(2027, 2, 9)),
        ("Del 23 de diciembre al 03 de enero de 2027", date(2026, 12, 23), date(2027, 1, 3)),
        ("12 DE OCTUBRE DE 2026", date(2026, 10, 12), date(2026, 10, 12)),
    ],
)
def test_interpreta_formas_del_calendario(texto, inicio, fin):
    assert interpretar_rango(texto) == RangoFechas(inicio, fin)


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "MATRICULACIÓN",
        "NOTA 1: El VA - DFAP determina las fechas",
        "31 de febrero de 2026",
        "Del 20 al 10 de marzo de 2026",
        "Semana 7",
    ],
)
def test_rechaza_textos_que_no_son_fechas_validas(texto):
    assert interpretar_rango(texto) is None


def test_rango_cuenta_sus_dias():
    rango = interpretar_rango("Del 18 al 23 de mayo de 2026")

    assert rango.dias == 6
    assert rango.contiene(date(2026, 5, 20))
    assert not rango.contiene(date(2026, 5, 24))
