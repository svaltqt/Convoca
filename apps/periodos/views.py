from django.urls import reverse, reverse_lazy

from config.views import (
    CrearMaestraView,
    DesactivarView,
    EditarMaestraView,
    ListaConBusquedaView,
    ReactivarView,
)
from .forms import PeriodoForm
from .models import Periodo


class PeriodoListView(ListaConBusquedaView):
    model = Periodo
    template_name = "periodos/periodo_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains",)
    encabezados = ("Nombre", "Inicio", "Fin", "Cierre de propuestas", "Cupo mínimo", "Estado", "Acciones")
    texto_crear = "Nuevo periodo"
    campo_activo = "abierto"
    url_name_editar = "periodos:periodo_editar"
    url_name_desactivar = "periodos:periodo_desactivar"
    url_name_reactivar = "periodos:periodo_reactivar"

    def get_url_crear(self):
        return reverse("periodos:periodo_crear")

    def fila(self, periodo):
        acciones = self.construir_acciones(periodo, periodo.abierto)
        return [
            periodo.nombre,
            periodo.inicio,
            periodo.fin,
            periodo.fecha_cierre_propuestas,
            periodo.cupo_minimo,
            "Abierto" if periodo.abierto else "Cerrado",
            acciones,
        ]


class PeriodoCreateView(CrearMaestraView):
    model = Periodo
    form_class = PeriodoForm
    template_name = "periodos/periodo_formulario.html"
    success_url = reverse_lazy("periodos:periodo_lista")
    success_message = "Se creó el periodo «%(nombre)s»."


class PeriodoUpdateView(EditarMaestraView):
    model = Periodo
    form_class = PeriodoForm
    template_name = "periodos/periodo_formulario.html"
    success_url = reverse_lazy("periodos:periodo_lista")
    success_message = "Se actualizó el periodo «%(nombre)s»."


class PeriodoDesactivarView(DesactivarView):
    model = Periodo
    campo_activo = "abierto"
    template_name = "periodos/periodo_confirmar_desactivar.html"
    success_url = reverse_lazy("periodos:periodo_lista")
    mensaje_exito = "Se desactivó el periodo."


class PeriodoReactivarView(ReactivarView):
    model = Periodo
    campo_activo = "abierto"
    template_name = "periodos/periodo_confirmar_reactivar.html"
    success_url = reverse_lazy("periodos:periodo_lista")
    mensaje_exito = "Se reactivó el periodo."