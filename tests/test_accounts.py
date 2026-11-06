from datetime import date

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


def test_inicio_exige_login(client):
    respuesta = client.get(reverse("inicio"))

    assert respuesta.status_code == 302
    assert respuesta.url.startswith(reverse("login"))


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
