from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inicio(request):
    periodos = request.user.periodos.prefetch_related("materias")
    return render(request, "core/inicio.html", {"periodos": periodos})
