from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

#: nombres de los grupos de roles (tarea 1.3). Todo usuario autenticado que
#: no pertenece al grupo Administrador se trata como Estudiante por defecto.
NOMBRE_GRUPO_ADMINISTRADOR = "Administrador"
NOMBRE_GRUPO_ESTUDIANTE = "Estudiante"


class SoloAdministradoresMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe una vista a usuarios autenticados con is_staff."""

    def test_func(self):
        return self.request.user.is_staff


class SoloGrupoAdministradorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Restringe una vista a usuarios autenticados que pertenecen al grupo
    Administrador. La pertenencia al grupo es lo que otorga el acceso, sin
    importar is_staff: quien no pertenece al grupo recibe 403.
    """

    def test_func(self):
        return self.request.user.groups.filter(name=NOMBRE_GRUPO_ADMINISTRADOR).exists()
