from django.urls import reverse, reverse_lazy
from django.utils.html import format_html

from config.views import (
    CrearMaestraView,
    DesactivarView,
    EditarMaestraView,
    ListaConBusquedaView,
    ReactivarView,
)

from .forms import FacultadForm
from .models import Facultad


class FacultadListView(ListaConBusquedaView):
    model = Facultad
    template_name = "academico/facultad_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains",)
    encabezados = ("Nombre", "Estado", "Acciones")
    texto_crear = "Nueva facultad"

    def get_url_crear(self):
        return reverse("academico:facultad_crear")

    def fila(self, facultad):
        acciones = format_html(
            '<a href="{}">Editar</a>',
            reverse("academico:facultad_editar", args=[facultad.pk]),
        )
        if facultad.activa:
            enlace_estado = format_html(
                '<a href="{}" class="enlace-peligro">Desactivar</a>',
                reverse("academico:facultad_desactivar", args=[facultad.pk]),
            )
        else:
            enlace_estado = format_html(
                '<a href="{}">Reactivar</a>',
                reverse("academico:facultad_reactivar", args=[facultad.pk]),
            )
        acciones = format_html("{} · {}", acciones, enlace_estado)
        return [facultad.nombre, "Activa" if facultad.activa else "Inactiva", acciones]


class FacultadCreateView(CrearMaestraView):
    model = Facultad
    form_class = FacultadForm
    template_name = "academico/facultad_formulario.html"
    success_url = reverse_lazy("academico:facultad_lista")
    success_message = "Se creó la facultad «%(nombre)s»."


class FacultadUpdateView(EditarMaestraView):
    model = Facultad
    form_class = FacultadForm
    template_name = "academico/facultad_formulario.html"
    success_url = reverse_lazy("academico:facultad_lista")
    success_message = "Se actualizó la facultad «%(nombre)s»."


class FacultadDesactivarView(DesactivarView):
    model = Facultad
    template_name = "academico/facultad_confirmar_desactivar.html"
    success_url = reverse_lazy("academico:facultad_lista")
    mensaje_exito = "Se desactivó la facultad."


class FacultadReactivarView(ReactivarView):
    model = Facultad
    template_name = "academico/facultad_confirmar_reactivar.html"
    success_url = reverse_lazy("academico:facultad_lista")
    mensaje_exito = "Se reactivó la facultad."
