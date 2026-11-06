from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F, Q


class Periodo(models.Model):
    """Periodo académico. Su fecha de inicio permite resolver fechas como "Semana 7"."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="periodos"
    )
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        ordering = ["-fecha_inicio"]
        constraints = [
            models.UniqueConstraint(fields=["usuario", "nombre"], name="periodo_unico_por_usuario"),
            models.CheckConstraint(
                condition=Q(fecha_fin__gt=F("fecha_inicio")), name="periodo_fechas_validas"
            ),
        ]

    def __str__(self) -> str:
        return self.nombre


class Materia(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name="materias")
    nombre = models.CharField(max_length=200)
    codigo = models.CharField(max_length=30, blank=True)
    docente = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(fields=["periodo", "nombre"], name="materia_unica_por_periodo"),
        ]

    def __str__(self) -> str:
        return self.nombre


class Silabo(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        EN_REVISION = "en_revision", "En revisión"
        CONFIRMADO = "confirmado", "Confirmado"
        ERROR = "error", "Error"

    class Formato(models.TextChoices):
        TABLA = "tabla", "Tabla"
        LISTA = "lista", "Lista"
        PARRAFO = "parrafo", "Párrafo"
        DESCONOCIDO = "desconocido", "Desconocido"

    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="silabos")
    archivo = models.FileField(
        upload_to="silabos/%Y/", validators=[FileExtensionValidator(["pdf"])]
    )
    hash_sha256 = models.CharField(max_length=64)
    estado = models.CharField(max_length=20, choices=Estado, default=Estado.PENDIENTE)
    formato_detectado = models.CharField(
        max_length=20, choices=Formato, default=Formato.DESCONOCIDO
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "sílabo"
        verbose_name_plural = "sílabos"
        constraints = [
            models.UniqueConstraint(
                fields=["materia", "hash_sha256"], name="silabo_unico_por_materia"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.materia} ({self.get_estado_display()})"
