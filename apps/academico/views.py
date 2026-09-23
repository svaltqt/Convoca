from django.urls import reverse, reverse_lazy

from config.views import (
    CrearMaestraView,
    DesactivarView,
    EditarMaestraView,
    ListaConBusquedaView,
    ReactivarView,
)

from .forms import AsignaturaForm, DocenteForm, FacultadForm, ProgramaForm
from .models import Asignatura, Docente, Facultad, Programa


class FacultadListView(ListaConBusquedaView):
    model = Facultad
    template_name = "academico/facultad_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains",)
    encabezados = ("Nombre", "Estado", "Acciones")
    texto_crear = "Nueva facultad"
    campo_activo = "activa"
    url_name_editar = "academico:facultad_editar"
    url_name_desactivar = "academico:facultad_desactivar"
    url_name_reactivar = "academico:facultad_reactivar"

    def get_url_crear(self):
        return reverse("academico:facultad_crear")

    def fila(self, facultad):
        acciones = self.construir_acciones(facultad, facultad.activa)
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


class ProgramaListView(ListaConBusquedaView):
    model = Programa
    template_name = "academico/programa_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains", "codigo__icontains")
    encabezados = ("Nombre", "Código", "Facultad", "Estado", "Acciones")
    texto_crear = "Nuevo programa"
    campo_activo = "activo"
    url_name_editar = "academico:programa_editar"
    url_name_desactivar = "academico:programa_desactivar"
    url_name_reactivar = "academico:programa_reactivar"
    campo_filtro_relacion = "facultad"
    etiqueta_filtro_relacion = "Facultad"

    def get_queryset(self):
        return super().get_queryset().select_related("facultad")

    def get_opciones_filtro_relacion(self):
        return Facultad.objects.filter(activa=True).order_by("nombre")

    def get_url_crear(self):
        return reverse("academico:programa_crear")

    def fila(self, programa):
        acciones = self.construir_acciones(programa, programa.activo)
        return [
            programa.nombre,
            programa.codigo,
            programa.facultad.nombre,
            "Activo" if programa.activo else "Inactivo",
            acciones,
        ]


class ProgramaCreateView(CrearMaestraView):
    model = Programa
    form_class = ProgramaForm
    template_name = "academico/programa_formulario.html"
    success_url = reverse_lazy("academico:programa_lista")
    success_message = "Se creó el programa «%(nombre)s»."


class ProgramaUpdateView(EditarMaestraView):
    model = Programa
    form_class = ProgramaForm
    template_name = "academico/programa_formulario.html"
    success_url = reverse_lazy("academico:programa_lista")
    success_message = "Se actualizó el programa «%(nombre)s»."


class ProgramaDesactivarView(DesactivarView):
    model = Programa
    campo_activo = "activo"
    template_name = "academico/programa_confirmar_desactivar.html"
    success_url = reverse_lazy("academico:programa_lista")
    mensaje_exito = "Se desactivó el programa."


class ProgramaReactivarView(ReactivarView):
    model = Programa
    campo_activo = "activo"
    template_name = "academico/programa_confirmar_reactivar.html"
    success_url = reverse_lazy("academico:programa_lista")
    mensaje_exito = "Se reactivó el programa."


class DocenteListView(ListaConBusquedaView):
    model = Docente
    template_name = "academico/docente_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains", "email__icontains")
    encabezados = ("Nombre", "Correo", "Disponible", "Estado", "Acciones")
    texto_crear = "Nuevo docente"
    campo_activo = "activo"
    url_name_editar = "academico:docente_editar"
    url_name_desactivar = "academico:docente_desactivar"
    url_name_reactivar = "academico:docente_reactivar"

    def get_url_crear(self):
        return reverse("academico:docente_crear")

    def fila(self, docente):
        acciones = self.construir_acciones(docente, docente.activo)
        return [
            docente.nombre,
            docente.email,
            "Sí" if docente.disponible else "No",
            "Activo" if docente.activo else "Inactivo",
            acciones,
        ]


class DocenteCreateView(CrearMaestraView):
    model = Docente
    form_class = DocenteForm
    template_name = "academico/docente_formulario.html"
    success_url = reverse_lazy("academico:docente_lista")
    success_message = "Se creó el docente «%(nombre)s»."


class DocenteUpdateView(EditarMaestraView):
    model = Docente
    form_class = DocenteForm
    template_name = "academico/docente_formulario.html"
    success_url = reverse_lazy("academico:docente_lista")
    success_message = "Se actualizó el docente «%(nombre)s»."


class DocenteDesactivarView(DesactivarView):
    model = Docente
    campo_activo = "activo"
    template_name = "academico/docente_confirmar_desactivar.html"
    success_url = reverse_lazy("academico:docente_lista")
    mensaje_exito = "Se desactivó el docente."


class DocenteReactivarView(ReactivarView):
    model = Docente
    campo_activo = "activo"
    template_name = "academico/docente_confirmar_reactivar.html"
    success_url = reverse_lazy("academico:docente_lista")
    mensaje_exito = "Se reactivó el docente."


class AsignaturaListView(ListaConBusquedaView):
    model = Asignatura
    template_name = "academico/asignatura_lista.html"
    ordering = ("nombre",)
    campos_busqueda = ("nombre__icontains", "codigo__icontains")
    encabezados = ("Nombre", "Código", "Programa", "Créditos", "Estado", "Acciones")
    texto_crear = "Nueva asignatura"
    campo_activo = "activa"
    url_name_editar = "academico:asignatura_editar"
    url_name_desactivar = "academico:asignatura_desactivar"
    url_name_reactivar = "academico:asignatura_reactivar"
    campo_filtro_relacion = "programa"
    etiqueta_filtro_relacion = "Programa"

    def get_url_crear(self):
        return reverse("academico:asignatura_crear")

    def get_opciones_filtro_relacion(self):
        return Programa.objects.filter(activo=True).order_by("nombre")

    def fila(self, asignatura):
        acciones = self.construir_acciones(asignatura, asignatura.activa)
        return [
            asignatura.nombre,
            asignatura.codigo,
            asignatura.programa.nombre,
            asignatura.creditos,
            "Activa" if asignatura.activa else "Inactiva",
            acciones,
        ]


class AsignaturaCreateView(CrearMaestraView):
    model = Asignatura
    form_class = AsignaturaForm
    template_name = "academico/asignatura_formulario.html"
    success_url = reverse_lazy("academico:asignatura_lista")
    success_message = "Se creó la asignatura «%(nombre)s»."


class AsignaturaUpdateView(EditarMaestraView):
    model = Asignatura
    form_class = AsignaturaForm
    template_name = "academico/asignatura_formulario.html"
    success_url = reverse_lazy("academico:asignatura_lista")
    success_message = "Se actualizó la asignatura «%(nombre)s»."


class AsignaturaDesactivarView(DesactivarView):
    model = Asignatura
    campo_activo = "activa"
    template_name = "academico/asignatura_confirmar_desactivar.html"
    success_url = reverse_lazy("academico:asignatura_lista")
    mensaje_exito = "Se desactivó la asignatura."


class AsignaturaReactivarView(ReactivarView):
    model = Asignatura
    campo_activo = "activa"
    template_name = "academico/asignatura_confirmar_reactivar.html"
    success_url = reverse_lazy("academico:asignatura_lista")
    mensaje_exito = "Se reactivó la asignatura."
