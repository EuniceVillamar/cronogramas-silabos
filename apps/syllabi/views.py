from django.shortcuts import render
from django.utils import timezone

from apps.exports.semana import leer_eventos, semana_de_ejemplo, semana_destacada
from apps.exports.views import CLAVE_ICS


def inicio(request):
    hoy = timezone.localdate()
    contexto = {"hoy": hoy}
    if not request.user.is_authenticated:
        contexto.update(semana=semana_de_ejemplo(), es_ejemplo=True)
        return render(request, "core/inicio.html", contexto)

    contexto["periodos"] = request.user.periodos.prefetch_related("materias")
    ics = request.session.get(CLAVE_ICS)
    if ics:
        contexto.update(semana=semana_destacada(leer_eventos(ics), hoy), tiene_calendario=True)
    return render(request, "core/inicio.html", contexto)
