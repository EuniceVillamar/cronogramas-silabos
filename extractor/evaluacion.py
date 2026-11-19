"""Medición de la precisión del extractor frente a un resultado etiquetado a mano."""

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .models import CalendarioAcademico


@dataclass(frozen=True)
class Metricas:
    correctas: int
    extraidas: int
    esperadas: int

    @property
    def precision(self) -> float:
        return self.correctas / self.extraidas if self.extraidas else 0.0

    @property
    def cobertura(self) -> float:
        return self.correctas / self.esperadas if self.esperadas else 0.0


def evaluar_calendario(calendario: CalendarioAcademico, esperado: Path) -> Metricas:
    """Una fecha es correcta si su inicio, fin y tipo coinciden con una fila esperada."""
    datos = json.loads(esperado.read_text(encoding="utf-8"))
    esperadas = Counter((e["inicio"], e["fin"], e["tipo"]) for e in datos["eventos"])
    extraidas = Counter(
        (e.rango.inicio.isoformat(), e.rango.fin.isoformat(), str(e.tipo))
        for e in calendario.eventos
    )
    correctas = sum((esperadas & extraidas).values())
    return Metricas(
        correctas=correctas,
        extraidas=sum(extraidas.values()),
        esperadas=sum(esperadas.values()),
    )
