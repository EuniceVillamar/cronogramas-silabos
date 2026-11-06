from django.contrib import admin

from .models import Actividad, Conflicto


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("titulo", "materia", "tipo", "fecha", "confianza", "origen", "revisada")
    list_filter = ("tipo", "origen", "revisada")


@admin.register(Conflicto)
class ConflictoAdmin(admin.ModelAdmin):
    list_display = ("periodo", "tipo", "severidad", "creado_en")
    list_filter = ("tipo", "severidad")
