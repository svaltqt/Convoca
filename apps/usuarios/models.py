from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _crear(self, email, password, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._crear(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._crear(email, password, **extra)


class Usuario(AbstractUser):
    username = None
    email = models.EmailField("correo institucional", unique=True)
    autorizo_datos = models.BooleanField("autorizó tratamiento de datos", default=False)
    fecha_autorizacion = models.DateTimeField(
        "fecha de autorización", null=True, blank=True
    )
    programa = models.ForeignKey(
        "academico.Programa",
        on_delete=models.PROTECT,
        verbose_name="programa",
        related_name="usuarios",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email

    @property
    def es_administrador(self):
        """
        Pertenece al grupo Administrador (tarea 1.3). Es lo que controla la
        visibilidad de las opciones de administrador en el menú (tarea 1.4);
        el acceso real a las vistas de maestras se resuelve por separado en
        config/views.py.
        """
        return self.groups.filter(name=settings.NOMBRE_GRUPO_ADMINISTRADOR).exists()
