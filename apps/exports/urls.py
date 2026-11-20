from django.urls import path

from .views import descargar_calendario, generar_calendario

urlpatterns = [
    path("", generar_calendario, name="generar_calendario"),
    path("descargar/", descargar_calendario, name="descargar_calendario"),
]
