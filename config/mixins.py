from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class SoloAdministradoresMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restringe una vista a usuarios autenticados con is_staff."""

    def test_func(self):
        return self.request.user.is_staff
