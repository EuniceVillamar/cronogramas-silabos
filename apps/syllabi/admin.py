from django.contrib import admin

from .models import Materia, Periodo, Silabo


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "usuario", "fecha_inicio", "fecha_fin")


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "periodo")


@admin.register(Silabo)
class SilaboAdmin(admin.ModelAdmin):
    list_display = ("materia", "estado", "formato_detectado", "creado_en")
    list_filter = ("estado", "formato_detectado")
