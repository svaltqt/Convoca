import operator
from functools import reduce

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin

from .mixins import SoloAdministradoresMixin, SoloGrupoAdministradorMixin

"""
Vistas base para las pantallas maestras (facultades, programas, asignaturas,
docentes, periodos, usuarios). Se escriben una vez aquí y cada maestra
hereda de ellas, indicando solo lo que cambia por modelo: campos de
búsqueda, encabezados de la tabla y cómo se arma cada fila.
"""


class ListaConBusquedaView(SoloGrupoAdministradorMixin, ListView):
    """
    Listado con búsqueda de texto (parámetro ``q``), filtro por estado,
    filtro opcional por una relación (FK) y paginación, listo para el
    parcial componentes/tabla_listado.html.

    Cada maestra declara:
      - model, template_name
      - campos_busqueda: lookups sobre los que buscar, p. ej. ["nombre__icontains"]
      - encabezados: encabezados de columna para la tabla
      - fila(self, objeto): celdas de una fila (lista de valores/HTML seguro).
        Para la celda de acciones, usar self.construir_acciones(objeto, activo).
      - url_name_editar / url_name_desactivar / url_name_reactivar: nombres
        de URL (con namespace) que usa construir_acciones()
      - get_url_crear() y texto_crear (opcionales, para el botón de creación)
      - campo_filtro_relacion / etiqueta_filtro_relacion y
        get_opciones_filtro_relacion() (opcionales, para filtrar por FK,
        p. ej. programas por facultad)
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

    #: nombres de URL (con namespace) para las acciones de fila. Los usa
    #: construir_acciones(); si una maestra arma sus acciones a mano, puede
    #: dejarlos en None.
    url_name_editar = None
    url_name_desactivar = None
    url_name_reactivar = None

    #: nombre del campo de relación (FK) por el que además se puede filtrar,
    #: p. ej. "facultad" en el listado de programas. None lo desactiva.
    campo_filtro_relacion = None
    etiqueta_filtro_relacion = None

    def get_estado(self):
        valor = self.request.GET.get("estado", self.estado_por_defecto)
        return valor if valor in self.valores_estado else self.estado_por_defecto

    def get_opciones_filtro_relacion(self):
        """Queryset de opciones para el <select> del filtro por relación."""
        return

    def get_valor_filtro_relacion(self):
        if not self.campo_filtro_relacion:
            return ""
        return self.request.GET.get(self.campo_filtro_relacion, "")

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

        valor_relacion = self.get_valor_filtro_relacion()
        if valor_relacion:
            queryset = queryset.filter(
                **{f"{self.campo_filtro_relacion}__pk": valor_relacion}
            )

        return queryset

    def fila(self, objeto):
        raise NotImplementedError(
            "Defina fila() para construir las celdas de cada registro."
        )

    def construir_acciones(self, objeto, activo):
        """Celda de acciones estándar: Editar + Desactivar o Reactivar.

        Las clases accion--editar / accion--desactivar / accion--reactivar
        permiten a estilos.css añadir el icono correspondiente con una
        máscara CSS; el texto del enlace se mantiene como nombre accesible.
        """
        acciones = format_html(
            '<a href="{}" class="accion accion--editar">Editar</a>',
            reverse(self.url_name_editar, args=[objeto.pk]),
        )
        if activo:
            enlace_estado = format_html(
                '<a href="{}" class="accion accion--desactivar enlace-peligro">Desactivar</a>',
                reverse(self.url_name_desactivar, args=[objeto.pk]),
            )
        else:
            enlace_estado = format_html(
                '<a href="{}" class="accion accion--reactivar">Reactivar</a>',
                reverse(self.url_name_reactivar, args=[objeto.pk]),
            )
        return format_html('<span class="tabla-acciones">{}{}</span>', acciones, enlace_estado)

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
        if self.campo_filtro_relacion:
            contexto["filtro_relacion"] = {
                "campo": self.campo_filtro_relacion,
                "etiqueta": self.etiqueta_filtro_relacion or self.campo_filtro_relacion,
                "valor": self.get_valor_filtro_relacion(),
                "opciones": self.get_opciones_filtro_relacion(),
            }
        else:
            contexto["filtro_relacion"] = None
        return contexto


class CrearMaestraView(SoloAdministradoresMixin, SuccessMessageMixin, CreateView):
    """Creación de un registro de maestra: solo administradores."""


class EditarMaestraView(SoloAdministradoresMixin, SuccessMessageMixin, UpdateView):
    """Edición de un registro de maestra: solo administradores."""


class CambiarEstadoView(
    SoloGrupoAdministradorMixin, SingleObjectMixin, TemplateResponseMixin, View
):
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
            raise ImproperlyConfigured(
                "Defina success_url en la vista de cambio de estado."
            )
        return self.success_url


class DesactivarView(CambiarEstadoView):
    """Borrado lógico: pone el campo de estado en False."""

    valor_destino = False
    mensaje_exito = "Se desactivó correctamente."


class ReactivarView(CambiarEstadoView):
    """Reactivación: pone el campo de estado en True."""

    valor_destino = True
    mensaje_exito = "Se reactivó correctamente."
