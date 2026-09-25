from django.db import models


class Periodo(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    inicio = models.DateField("inicio")
    fin = models.DateField("fin")
    fecha_cierre_propuestas = models.DateField("fecha de cierre de propuestas")
    cupo_minimo = models.PositiveSmallIntegerField("cupo mínimo", default=20)
    abierto = models.BooleanField("abierto", default=True)

    class Meta:
        verbose_name = "periodo"
        verbose_name_plural = "periodos"

    def __str__(self) -> str:
        return str(self.nombre)
