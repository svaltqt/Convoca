from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import FormularioLogin, RegistroForm
from .models import Usuario


class EntrarView(LoginView):
    template_name = "usuarios/entrar.html"
    authentication_form = FormularioLogin


class SalirView(LogoutView):
    """Cierre de sesión: Django solo acepta POST para esta acción."""


class RegistroView(CreateView):
    model = Usuario
    form_class = RegistroForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("usuarios:entrar")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(
            self.request, "Tu cuenta fue creada. Ya puedes iniciar sesión."
        )
        return respuesta


class PoliticaDatosView(TemplateView):
    template_name = "usuarios/politica_datos.html"
