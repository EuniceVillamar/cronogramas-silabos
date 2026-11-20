from datetime import date
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.syllabi.models import Periodo

pytestmark = pytest.mark.django_db
Usuario = get_user_model()


def test_registro_crea_usuario_e_inicia_sesion(client):
    respuesta = client.post(
        reverse("registro"),
        {
            "username": "ana",
            "email": "ana@example.com",
            "password1": "clave-de-prueba-123",
            "password2": "clave-de-prueba-123",
        },
    )

    assert respuesta.status_code == 302
    assert Usuario.objects.filter(username="ana").exists()
    assert client.get(reverse("inicio")).status_code == 200


def test_inicio_sin_cuenta_muestra_la_portada_con_semana_de_ejemplo(client):
    respuesta = client.get(reverse("inicio"))

    contenido = respuesta.content.decode()
    assert respuesta.status_code == 200
    assert "Ejemplo: CII 2026-2027" in contenido
    assert reverse("registro") in contenido
    assert "Tus periodos" not in contenido


def test_inicio_muestra_la_semana_del_calendario_generado(client):
    client.force_login(Usuario.objects.create_user("ana"))
    calendario = Path(__file__).parent / "fixtures" / "calendarios" / "ug-cii-2026-2027.pdf"
    with calendario.open("rb") as archivo:
        client.post(reverse("generar_calendario"), {"calendario": archivo, "dias_repaso": 7})

    contenido = client.get(reverse("inicio")).content.decode()

    assert "Descargar .ics" in contenido
    assert "dia__fecha" in contenido


def test_inicio_solo_muestra_periodos_propios(client):
    ana = Usuario.objects.create_user("ana")
    luis = Usuario.objects.create_user("luis")
    fechas = {"fecha_inicio": date(2027, 3, 1), "fecha_fin": date(2027, 7, 1)}
    Periodo.objects.create(usuario=ana, nombre="Periodo de Ana", **fechas)
    Periodo.objects.create(usuario=luis, nombre="Periodo de Luis", **fechas)

    client.force_login(ana)
    contenido = client.get(reverse("inicio")).content.decode()

    assert "Periodo de Ana" in contenido
    assert "Periodo de Luis" not in contenido
