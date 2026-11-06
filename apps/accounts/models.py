from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """Modelo propio desde el inicio: cambiarlo después obliga a migraciones difíciles."""

    class Meta(AbstractUser.Meta):
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
