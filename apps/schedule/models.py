from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from apps.syllabi.models import Materia, Periodo, Silabo


class Actividad(models.Model):
    class Tipo(models.TextChoices):
        EXAMEN = "examen", "Examen"
        ENTREGA = "entrega", "Entrega"
        PROYECTO = "proyecto", "Proyecto"
        OTRO = "otro", "Otro"

    class Origen(models.TextChoices):
        REGLA = "regla", "Regla"
        IA = "ia", "IA"
        MANUAL = "manual", "Manual"

    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="actividades")
    silabo = models.ForeignKey(
        Silabo, on_delete=models.SET_NULL, null=True, blank=True, related_name="actividades"
    )
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=Tipo, default=Tipo.OTRO)
    fecha = models.DateField(
        null=True, blank=True, help_text="Vacía si la extracción no pudo resolverla."
    )
    fecha_texto = models.CharField(
        max_length=100, blank=True, help_text='Texto original del sílabo, como "Semana 7".'
    )
    ponderacion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    confianza = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
    )
    origen = models.CharField(max_length=10, choices=Origen, default=Origen.MANUAL)
    revisada = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha", "titulo"]
        verbose_name_plural = "actividades"
        indexes = [models.Index(fields=["materia", "fecha"])]
        constraints = [
            # Nada entra al calendario sin fecha: revisar exige haberla resuelto.
            models.CheckConstraint(
                condition=Q(revisada=False) | Q(fecha__isnull=False),
                name="actividad_revisada_con_fecha",
            ),
        ]

    def __str__(self) -> str:
        return self.titulo


class Conflicto(models.Model):
    class Tipo(models.TextChoices):
        MISMO_DIA = "mismo_dia", "Mismo día"
        VENTANA_48H = "ventana_48h", "Ventana de 48 horas"

    class Severidad(models.TextChoices):
        CONFLICTO = "conflicto", "Conflicto"
        ADVERTENCIA = "advertencia", "Advertencia"

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name="conflictos")
    actividades = models.ManyToManyField(Actividad, related_name="conflictos")
    tipo = models.CharField(max_length=20, choices=Tipo)
    severidad = models.CharField(max_length=20, choices=Severidad)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.get_severidad_display()}: {self.get_tipo_display()}"
