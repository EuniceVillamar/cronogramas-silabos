from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.urls import reverse
from icalendar import Calendar

pytestmark = pytest.mark.django_db
CALENDARIO = Path(__file__).parent / "fixtures" / "calendarios" / "ug-cii-2026-2027.pdf"


@pytest.fixture
def cliente(client):
    client.force_login(get_user_model().objects.create_user("ana"))
    return client


def _pdf(ruta: Path) -> SimpleUploadedFile:
    return SimpleUploadedFile(ruta.name, ruta.read_bytes(), content_type="application/pdf")


def test_generar_exige_login(client):
    respuesta = client.get(reverse("generar_calendario"))

    assert respuesta.status_code == 302
    assert respuesta.url.startswith(reverse("login"))


def test_genera_vista_previa_y_descarga_el_ics(cliente):
    respuesta = cliente.post(
        reverse("generar_calendario"), {"calendario": _pdf(CALENDARIO), "dias_repaso": 7}
    )

    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    assert "Calendario CII 2026-2027" in contenido
    assert "Exámenes del primer parcial" in contenido
    assert "Probablemente es 09/10/2026" in contenido

    descarga = cliente.get(reverse("descargar_calendario"))
    assert descarga["Content-Type"].startswith("text/calendar")
    assert 'filename="calendario-cii-2026-2027.ics"' in descarga["Content-Disposition"]
    eventos = Calendar.from_ical(descarga.content).walk("VEVENT")
    assert any(str(e["SUMMARY"]) == "Exámenes del segundo parcial" for e in eventos)


def test_avisa_cuando_un_silabo_no_tiene_unidades(cliente):
    respuesta = cliente.post(
        reverse("generar_calendario"),
        {"calendario": _pdf(CALENDARIO), "silabos": [_pdf(CALENDARIO)], "dias_repaso": 7},
    )

    assert respuesta.status_code == 200
    assert "no parece un sílabo" in respuesta.content.decode()


def test_rechaza_archivos_que_no_son_pdf(cliente):
    falso = SimpleUploadedFile("calendario.pdf", b"hola", content_type="application/pdf")

    respuesta = cliente.post(reverse("generar_calendario"), {"calendario": falso, "dias_repaso": 7})

    assert respuesta.status_code == 200
    assert "no es un PDF válido" in respuesta.content.decode()


def test_descargar_sin_generar_redirige_al_formulario(cliente):
    respuesta = cliente.get(reverse("descargar_calendario"))

    assert respuesta.status_code == 302
    assert respuesta.url == reverse("generar_calendario")


def test_comando_guarda_el_ics(tmp_path):
    salida = tmp_path / "calendario.ics"

    call_command("generar_calendario", str(CALENDARIO), salida=salida)

    eventos = Calendar.from_ical(salida.read_bytes()).walk("VEVENT")
    assert len(eventos) > 10
