import operator
from functools import reduce

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin

from .mixins import SoloAdministradoresMixin

"""
Vistas base para las pantallas maestras (facultades, programas, asignaturas,
docentes, periodos, usuarios). Se escriben una vez aquí y cada maestra
hereda de ellas, indicando solo lo que cambia por modelo: campos de
búsqueda, encabezados de la tabla y cómo se arma cada fila.
"""


class ListaConBusquedaView(SoloAdministradoresMixin, ListView):
    """
    Listado con búsqueda de texto (parámetro ``q``) y paginación, listo
    para el parcial componentes/tabla_listado.html.

    Cada maestra declara:
      - model, template_name
      - campos_busqueda: lookups sobre los que buscar, p. ej. ["nombre__icontains"]
      - encabezados: encabezados de columna para la tabla
      - fila(self, objeto): celdas de una fila (lista de valores/HTML seguro)
      - get_url_crear() y texto_crear (opcionales, para el botón de creación)
    """

    paginate_by = 20
    context_object_name = "objetos"
    campos_busqueda = ()
    encabezados = ()
    texto_crear = "Nuevo"
    mensaje_vacio = "No hay registros para mostrar."

    #: nombre del campo booleano de borrado lógico (activa/activo) sobre el
    #: que se aplica el filtro de estado. ``None`` desactiva el filtro para
    #: maestras que no tengan ese campo.
    campo_activo = "activa"
    valores_estado = ("activas", "inactivas", "todas")
    estado_por_defecto = "activas"

    def get_estado(self):
        valor = self.request.GET.get("estado", self.estado_por_defecto)
        return valor if valor in self.valores_estado else self.estado_por_defecto

    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda and self.campos_busqueda:
            condiciones = [Q(**{campo: busqueda}) for campo in self.campos_busqueda]
            queryset = queryset.filter(reduce(operator.or_, condiciones))

        if self.campo_activo:
            estado = self.get_estado()
            if estado == "activas":
                queryset = queryset.filter(**{self.campo_activo: True})
            elif estado == "inactivas":
                queryset = queryset.filter(**{self.campo_activo: False})
        return queryset

    def fila(self, objeto):
        raise NotImplementedError("Defina fila() para construir las celdas de cada registro.")

    def get_url_crear(self):
        return None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busqueda"] = self.request.GET.get("q", "")
        contexto["estado"] = self.get_estado() if self.campo_activo else None
        contexto["encabezados"] = self.encabezados
        contexto["filas"] = [self.fila(objeto) for objeto in contexto["page_obj"]]
        contexto["url_crear"] = self.get_url_crear()
        contexto["texto_crear"] = self.texto_crear
        contexto["mensaje_vacio"] = self.mensaje_vacio
        return contexto


class CrearMaestraView(SoloAdministradoresMixin, SuccessMessageMixin, CreateView):
    """Creación de un registro de maestra: solo administradores."""


class EditarMaestraView(SoloAdministradoresMixin, SuccessMessageMixin, UpdateView):
    """Edición de un registro de maestra: solo administradores."""


class CambiarEstadoView(SoloAdministradoresMixin, SingleObjectMixin, TemplateResponseMixin, View):
    """
    Cambio de estado lógico genérico (activar o desactivar): nunca elimina
    el registro, solo escribe ``valor_destino`` en el campo indicado en
    ``campo_activo``. GET muestra la confirmación, POST aplica el cambio.

    Cada maestra declara: model, campo_activo (si no es "activa"),
    template_name y success_url.
    """

    campo_activo = "activa"
    valor_destino = False
    success_url = None
    mensaje_exito = "Se actualizó el estado correctamente."

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(object=self.object))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        setattr(self.object, self.campo_activo, self.valor_destino)
        self.object.save(update_fields=[self.campo_activo])
        messages.success(request, self.mensaje_exito)
        return redirect(self.get_success_url())

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured("Defina success_url en la vista de cambio de estado.")
        return self.success_url


class DesactivarView(CambiarEstadoView):
    """Borrado lógico: pone el campo de estado en False."""

    valor_destino = False
    mensaje_exito = "Se desactivó correctamente."


class ReactivarView(CambiarEstadoView):
    """Reactivación: pone el campo de estado en True."""

    valor_destino = True
    mensaje_exito = "Se reactivó correctamente."
