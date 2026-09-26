from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from apps.academico.models import Programa
from config.views import (
    DesactivarView,
    EditarMaestraView,
    ListaConBusquedaView,
    ReactivarView,
)

from .forms import FormularioLogin, RegistroForm, UsuarioForm
from .models import Usuario
from .services import eliminar_cuenta


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


class PerfilView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Perfil del propio usuario (tarea 1.6 / HU-17, primer criterio): ver y
    editar nombre, apellido y programa. Correo y autorización de datos no
    son editables aquí. get_object() siempre devuelve request.user, sin
    depender de un pk en la URL, así que nadie puede ver o editar el
    perfil de otra cuenta desde esta vista, ni siquiera un administrador.
    """

    model = Usuario
    form_class = UsuarioForm
    template_name = "usuarios/perfil.html"
    success_url = reverse_lazy("usuarios:perfil")
    success_message = "Se actualizó tu perfil."

    def get_object(self, queryset=None):
        return self.request.user


class EliminarCuentaView(LoginRequiredMixin, TemplateView):
    """
    GET muestra la confirmación; solo el POST del botón de confirmar
    elimina la cuenta, para evitar una eliminación por un clic accidental.
    Siempre actúa sobre request.user.
    """

    template_name = "usuarios/eliminar_cuenta.html"

    def post(self, request, *args, **kwargs):
        eliminar_cuenta(request.user)
        logout(request)
        messages.success(request, "Tu cuenta fue eliminada.")
        return redirect("inicio")


class UsuarioListView(ListaConBusquedaView):
    """
    Maestra de usuarios (HU-07): solo consulta, edición limitada y cambio
    de estado. No hay creación aquí — las cuentas solo se crean por
    registro, para no saltar la autorización de tratamiento de datos.
    """

    model = Usuario
    template_name = "usuarios/usuario_lista.html"
    ordering = ("first_name", "last_name")
    campos_busqueda = ("first_name__icontains", "last_name__icontains", "email__icontains")
    encabezados = ("Nombre", "Correo", "Programa", "Autorización de datos", "Estado", "Acciones")
    campo_activo = "is_active"
    url_name_editar = "usuarios:usuario_editar"
    url_name_desactivar = "usuarios:usuario_desactivar"
    url_name_reactivar = "usuarios:usuario_reactivar"
    campo_filtro_relacion = "programa"
    etiqueta_filtro_relacion = "Programa"

    def get_queryset(self):
        return super().get_queryset().select_related("programa")

    def get_opciones_filtro_relacion(self):
        return Programa.objects.filter(activo=True).order_by("nombre")

    def fila(self, usuario):
        acciones = self.construir_acciones(usuario, usuario.is_active)
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip() or "—"
        return [
            nombre_completo,
            usuario.email,
            usuario.programa.nombre if usuario.programa else "—",
            "Sí" if usuario.autorizo_datos else "No",
            "Activo" if usuario.is_active else "Inactivo",
            acciones,
        ]


class UsuarioUpdateView(EditarMaestraView):
    model = Usuario
    form_class = UsuarioForm
    template_name = "usuarios/usuario_formulario.html"
    success_url = reverse_lazy("usuarios:usuario_lista")
    success_message = "Se actualizó la cuenta de «%(first_name)s %(last_name)s»."


class UsuarioDesactivarView(DesactivarView):
    model = Usuario
    campo_activo = "is_active"
    template_name = "usuarios/usuario_confirmar_desactivar.html"
    success_url = reverse_lazy("usuarios:usuario_lista")
    mensaje_exito = "Se desactivó la cuenta."


class UsuarioReactivarView(ReactivarView):
    model = Usuario
    campo_activo = "is_active"
    template_name = "usuarios/usuario_confirmar_reactivar.html"
    success_url = reverse_lazy("usuarios:usuario_lista")
    mensaje_exito = "Se reactivó la cuenta."
