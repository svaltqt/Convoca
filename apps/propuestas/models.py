from django.conf import settings
from django.db import models


class Propuesta(models.Model):
    class Estado(models.TextChoices):
        ABIERTA = "ABIERTA", "Abierta"
        QUORUM = "QUORUM", "Quórum"
        RADICADA = "RADICADA", "Radicada"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    asignatura = models.ForeignKey(
        "academico.Asignatura",
        on_delete=models.PROTECT,
        verbose_name="asignatura",
        related_name="propuestas",
    )
    periodo = models.ForeignKey(
        "periodos.Periodo",
        on_delete=models.PROTECT,
        verbose_name="periodo",
        related_name="propuestas",
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="creador",
        related_name="propuestas_creadas",
    )
    docente = models.ForeignKey(
        "academico.Docente",
        on_delete=models.PROTECT,
        verbose_name="docente",
        related_name="propuestas",
        null=True,
        blank=True,
    )
    estado = models.CharField(
        "estado",
        max_length=10,
        choices=Estado.choices,
        default=Estado.ABIERTA,
    )
    creada = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "propuesta"
        verbose_name_plural = "propuestas"
        constraints = [
            models.UniqueConstraint(
                fields=["asignatura", "periodo"],
                condition=~models.Q(estado="RECHAZADA"),
                name="unica_propuesta_activa_por_asignatura_periodo",
            ),
        ]

    def __str__(self):
        return f"{self.asignatura} - {self.periodo}"


class Adhesion(models.Model):
    propuesta = models.ForeignKey(
        Propuesta,
        on_delete=models.PROTECT,
        verbose_name="propuesta",
        related_name="adhesiones",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="usuario",
        related_name="adhesiones",
    )
    creada = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "adhesión"
        verbose_name_plural = "adhesiones"
        constraints = [
            models.UniqueConstraint(
                fields=["propuesta", "usuario"],
                name="unica_adhesion_por_propuesta_y_usuario",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.propuesta}"
