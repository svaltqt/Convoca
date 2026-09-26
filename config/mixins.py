from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


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
        return self.request.user.groups.filter(
            name=settings.NOMBRE_GRUPO_ADMINISTRADOR
        ).exists()
