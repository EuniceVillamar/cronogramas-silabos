from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.schedule.models import Actividad
from apps.syllabi.models import Materia, Periodo, Silabo

pytestmark = pytest.mark.django_db


@pytest.fixture
def periodo():
    usuario = get_user_model().objects.create_user("ana")
    return Periodo.objects.create(
        usuario=usuario,
        nombre="2027-I",
        fecha_inicio=date(2027, 3, 1),
        fecha_fin=date(2027, 7, 1),
    )


@pytest.fixture
def materia(periodo):
    return Materia.objects.create(periodo=periodo, nombre="Gestión de la Configuración")


def test_periodo_rechaza_fin_anterior_al_inicio(periodo):
    with pytest.raises(IntegrityError):
        Periodo.objects.create(
            usuario=periodo.usuario,
            nombre="Invertido",
            fecha_inicio=date(2027, 7, 1),
            fecha_fin=date(2027, 3, 1),
        )


def test_silabo_rechaza_mismo_archivo_en_la_materia(materia):
    Silabo.objects.create(materia=materia, archivo="a.pdf", hash_sha256="a" * 64)

    with pytest.raises(IntegrityError):
        Silabo.objects.create(materia=materia, archivo="b.pdf", hash_sha256="a" * 64)


def test_actividad_sin_fecha_queda_pendiente(materia):
    actividad = Actividad.objects.create(materia=materia, titulo="Parcial", fecha_texto="Semana 7")

    assert actividad.revisada is False


def test_actividad_revisada_exige_fecha(materia):
    with pytest.raises(IntegrityError):
        Actividad.objects.create(materia=materia, titulo="Parcial", revisada=True)
