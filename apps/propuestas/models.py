from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class TransicionInvalidaError(Exception):
    """La propuesta no puede realizar la transición de estado solicitada."""


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

    @property
    def total_adhesiones(self):
        """Retorna el total de adhesiones a esta propuesta."""
        return self.adhesiones.count()

    def clean(self):
        """
        Regla 4: condiciones para crear una propuesta. Solo aplican al crearla;
        una propuesta existente debe poder cambiar de estado aunque luego el
        periodo cierre o la asignatura se desactive.
        """
        if not self._state.adding:
            return

        if self.asignatura and not self.asignatura.activa:
            raise ValidationError(
                {"asignatura": "No se puede crear una propuesta con una asignatura inactiva."}
            )

        if self.periodo and not self.periodo.abierto:
            raise ValidationError(
                {"periodo": "No se puede crear una propuesta en un periodo cerrado."}
            )

        if self.periodo and self.periodo.fecha_cierre_propuestas < timezone.localdate():
            raise ValidationError(
                {"periodo": "No se puede crear una propuesta después de la fecha de cierre de propuestas."}
            )

    def save(self, *args, **kwargs):
        nueva = self._state.adding
        self.full_clean(validate_constraints=False)
        with transaction.atomic():
            super().save(*args, **kwargs)
            if nueva and self.estado == Propuesta.Estado.ABIERTA:
                Adhesion.objects.create(propuesta=self, usuario=self.creador)

    def cambiar_estado(self, nuevo_estado, *, automatico=False):
        permitidas = {
            (self.Estado.QUORUM, self.Estado.RADICADA),
            (self.Estado.RADICADA, self.Estado.APROBADA),
            (self.Estado.RADICADA, self.Estado.RECHAZADA),
        }
        if automatico:
            permitidas |= {
                (self.Estado.ABIERTA, self.Estado.QUORUM),
                (self.Estado.QUORUM, self.Estado.ABIERTA),
            }
        if (self.estado, nuevo_estado) not in permitidas:
            raise TransicionInvalidaError(
                f"No se puede cambiar de {self.estado} a {nuevo_estado}."
            )
        self.estado = nuevo_estado
        self.save(update_fields=["estado"])

    def recalcular_estado_tras_retiro(self):
        """Regla 15: QUORUM vuelve a ABIERTA si queda por debajo del cupo."""
        if (
            self.estado == self.Estado.QUORUM
            and self.adhesiones.count() < self.periodo.cupo_minimo
        ):
            self.cambiar_estado(self.Estado.ABIERTA, automatico=True)


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

    def clean(self):
        """Validaciones del modelo"""
        # Validar que el periodo esté abierto
        if self.propuesta and self.propuesta.periodo and not self.propuesta.periodo.abierto:
            raise ValidationError(
                {"propuesta": "No se puede adherirse a una propuesta cuyo periodo está cerrado."}
            )

        # Validar que no estemos después de la fecha de cierre de propuestas
        if (self.propuesta and self.propuesta.periodo and
            self.propuesta.periodo.fecha_cierre_propuestas < timezone.now().date()):
            raise ValidationError(
                {"propuesta": "No se puede adherirse después de la fecha de cierre de propuestas."}
            )

        # Validar que el usuario haya autorizado el tratamiento de datos
        if self.usuario and not self.usuario.autorizo_datos:
            raise ValidationError(
                {"usuario": "No se puede adherirse sin autorización de tratamiento de datos."}
            )

        # Validar que la propuesta no esté en estado RADICADA, APROBADA o RECHAZADA
        if self.propuesta and self.propuesta.estado in [
            Propuesta.Estado.RADICADA,
            Propuesta.Estado.APROBADA,
            Propuesta.Estado.RECHAZADA
        ]:
            raise ValidationError(
                {"propuesta": "No se puede adherirse a una propuesta en estado RADICADA, APROBADA o RECHAZADA."}
            )

    def save(self, *args, **kwargs):
        nueva = self._state.adding
        self.full_clean(validate_constraints=False)
        with transaction.atomic():
            propuesta = Propuesta.objects.select_for_update().get(pk=self.propuesta_id)
            self.propuesta = propuesta
            self.full_clean(validate_constraints=False)
            super().save(*args, **kwargs)
            if nueva:
                total = propuesta.adhesiones.count()
                if total >= propuesta.periodo.cupo_minimo and propuesta.estado == Propuesta.Estado.ABIERTA:
                    propuesta.cambiar_estado(Propuesta.Estado.QUORUM, automatico=True)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            propuesta = Propuesta.objects.select_for_update().get(pk=self.propuesta_id)
            self.propuesta = propuesta
            if propuesta.estado not in (Propuesta.Estado.ABIERTA, Propuesta.Estado.QUORUM):
                raise ValidationError("No se puede retirar la adhesión de una propuesta radicada o posterior.")
            if not propuesta.periodo.abierto:
                raise ValidationError("No se puede retirar la adhesión si el periodo está cerrado.")
            result = super().delete(*args, **kwargs)
            propuesta.recalcular_estado_tras_retiro()
            return result
