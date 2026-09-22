from django.db import models


class Facultad(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "facultad"
        verbose_name_plural = "facultades"

    def __str__(self):
        return self.nombre


class Programa(models.Model):
    facultad = models.ForeignKey(
        Facultad,
        on_delete=models.PROTECT,
        verbose_name="facultad",
        related_name="programas",
    )
    nombre = models.CharField("nombre", max_length=150)
    codigo = models.CharField("código", max_length=20)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "programa"
        verbose_name_plural = "programas"

    def __str__(self):
        return self.nombre


class Asignatura(models.Model):
    programa = models.ForeignKey(
        Programa,
        on_delete=models.PROTECT,
        verbose_name="programa",
        related_name="asignaturas",
    )
    codigo = models.CharField("código", max_length=20)
    nombre = models.CharField("nombre", max_length=150)
    creditos = models.PositiveSmallIntegerField("créditos")
    activa = models.BooleanField("activa", default=True)

    class Meta:
        verbose_name = "asignatura"
        verbose_name_plural = "asignaturas"

    def __str__(self):
        return self.nombre


class Docente(models.Model):
    nombre = models.CharField("nombre", max_length=150)
    email = models.EmailField("correo")
    disponible = models.BooleanField("disponible", default=True)
    activo = models.BooleanField("activo", default=True)

    class Meta:
        verbose_name = "docente"
        verbose_name_plural = "docentes"

    def __str__(self):
        return self.nombre
