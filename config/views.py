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

    def get_queryset(self):
        queryset = super().get_queryset()
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda and self.campos_busqueda:
            condiciones = [Q(**{campo: busqueda}) for campo in self.campos_busqueda]
            queryset = queryset.filter(reduce(operator.or_, condiciones))
        return queryset

    def fila(self, objeto):
        raise NotImplementedError("Defina fila() para construir las celdas de cada registro.")

    def get_url_crear(self):
        return None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busqueda"] = self.request.GET.get("q", "")
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


class DesactivarView(SoloAdministradoresMixin, SingleObjectMixin, TemplateResponseMixin, View):
    """
    Borrado lógico genérico: nunca elimina el registro, solo apaga el campo
    indicado en ``campo_activo``. GET muestra la confirmación, POST aplica
    el cambio.

    Cada maestra declara: model, campo_activo (si no es "activa"),
    template_name y success_url.
    """

    campo_activo = "activa"
    success_url = None
    mensaje_exito = "Se desactivó correctamente."

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(object=self.object))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        setattr(self.object, self.campo_activo, False)
        self.object.save(update_fields=[self.campo_activo])
        messages.success(request, self.mensaje_exito)
        return redirect(self.get_success_url())

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured("Defina success_url en la vista de desactivación.")
        return self.success_url
