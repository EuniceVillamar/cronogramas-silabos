from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify

from .forms import GenerarCalendarioForm
from .services import ArchivoIlegible, generar_planificacion

CLAVE_ICS = "calendario_ics"
CLAVE_NOMBRE = "calendario_nombre"


@login_required
def generar_calendario(request):
    form = GenerarCalendarioForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            plan, contenido = generar_planificacion(
                form.cleaned_data["calendario"],
                form.cleaned_data["silabos"],
                form.cleaned_data["dias_repaso"],
            )
        except ArchivoIlegible as error:
            form.add_error("calendario", str(error))
        else:
            request.session[CLAVE_ICS] = contenido.decode("utf-8")
            request.session[CLAVE_NOMBRE] = f"calendario-{slugify(plan.periodo)}.ics"
            return render(request, "exports/resultado.html", {"plan": plan})
    return render(request, "exports/generar.html", {"form": form})


@login_required
def descargar_calendario(request):
    contenido = request.session.get(CLAVE_ICS)
    if not contenido:
        messages.info(request, "Primero genera tu calendario.")
        return redirect("generar_calendario")
    respuesta = HttpResponse(contenido, content_type="text/calendar; charset=utf-8")
    nombre = request.session.get(CLAVE_NOMBRE, "calendario.ics")
    respuesta["Content-Disposition"] = f'attachment; filename="{nombre}"'
    return respuesta
