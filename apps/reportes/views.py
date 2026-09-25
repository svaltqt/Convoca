from datetime import date

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, TemplateView

from apps.academico.models import Facultad
from apps.propuestas.models import Adhesion, Propuesta
from config.mixins import SoloAdministradoresMixin


def construir_facultades_con_datos(facultades):
    """Agrupa las propuestas activas por facultad con sus métricas de quórum.

    Excluye propuestas RECHAZADA y las de periodos cerrados o con
    fecha_cierre_propuestas vencida. Para cada facultad calcula el total de
    interesados, el cupo mínimo acumulado y el porcentaje de avance.
    """
    hoy = date.today()
    facultades_con_datos = []
    for facultad in facultades:
        propuestas_info = []
        total_interesados_facultad = 0
        total_cupo_minimo_facultad = 0

        for programa in facultad.programas.filter(activo=True):
            for asignatura in programa.asignaturas.filter(activa=True):
                for propuesta in asignatura.propuestas.exclude(
                    estado=Propuesta.Estado.RECHAZADA
                ).select_related("periodo"):
                    # Solo propuestas de periodos abiertos y no vencidos
                    if not propuesta.periodo.abierto:
                        continue
                    if propuesta.periodo.fecha_cierre_propuestas < hoy:
                        continue

                    total_adhesiones = propuesta.adhesiones.count()
                    cupo_minimo = propuesta.periodo.cupo_minimo
                    porcentaje = min(
                        int(total_adhesiones * 100 / max(cupo_minimo, 1)), 100
                    )

                    # Días restantes del periodo (hasta fin del periodo)
                    dias_restantes = max((propuesta.periodo.fin - hoy).days, 0)

                    propuestas_info.append(
                        {
                            "propuesta": propuesta,
                            "asignatura": asignatura,
                            "programa": programa,
                            "periodo": propuesta.periodo,
                            "total_interesados": total_adhesiones,
                            "cupo_minimo": cupo_minimo,
                            "porcentaje": porcentaje,
                            "dias_restantes": dias_restantes,
                            "estado": propuesta.estado,
                            "estado_display": propuesta.get_estado_display(),
                        }
                    )

                    total_interesados_facultad += total_adhesiones
                    total_cupo_minimo_facultad += cupo_minimo

        if propuestas_info:
            porcentaje_facultad = min(
                int(
                    total_interesados_facultad
                    * 100
                    / max(total_cupo_minimo_facultad, 1)
                ),
                100,
            )
            facultades_con_datos.append(
                {
                    "facultad": facultad,
                    "propuestas": propuestas_info,
                    "total_interesados": total_interesados_facultad,
                    "total_cupo_minimo": total_cupo_minimo_facultad,
                    "porcentaje": porcentaje_facultad,
                }
            )

    return facultades_con_datos


def obtener_facultades_con_propuestas():
    """Facultades activas con sus cadenas programa → asignatura → propuesta."""
    return (
        Facultad.objects.filter(activa=True)
        .prefetch_related(
            "programas__asignaturas__propuestas__periodo",
            "programas__asignaturas__propuestas__adhesiones",
        )
        .order_by("nombre")
    )


def generar_pdf_response(html, nombre_archivo):
    """Renderiza el HTML a PDF con xhtml2pdf y lo devuelve como descarga."""
    from io import BytesIO

    from xhtml2pdf import pisa

    buffer = BytesIO()
    resultado = pisa.CreatePDF(html, dest=buffer, encoding="utf-8")
    if resultado.err:
        return HttpResponse("No se pudo generar el PDF", status=500)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
    return response


class ReportesIndexView(SoloAdministradoresMixin, TemplateView):
    """Página de inicio de reportes administrativos."""

    template_name = "reportes/index.html"


class QuorumPorFacultadView(SoloAdministradoresMixin, ListView):
    """
    Reporte: Estado de quórum por facultad.

    Muestra las propuestas relevantes agrupadas por facultad con:
    - Cantidad de interesados/adhesiones
    - Porcentaje de avance frente al cupo_mínimo
    - Días restantes del periodo
    """

    template_name = "reportes/quorum_por_facultad.html"
    context_object_name = "facultades"

    def get_queryset(self):
        return obtener_facultades_con_propuestas()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["facultades_con_datos"] = construir_facultades_con_datos(
            contexto["facultades"]
        )
        contexto["hoy"] = date.today()
        return contexto


class QuorumPorFacultadPDFView(SoloAdministradoresMixin, TemplateView):
    """Exporta el estado de quórum por facultad a PDF usando xhtml2pdf."""

    template_name = "reportes/quorum_pdf.html"

    def get(self, request, *args, **kwargs):
        facultades_con_datos = construir_facultades_con_datos(
            obtener_facultades_con_propuestas()
        )
        html = render_to_string(
            self.template_name,
            {
                "facultades_con_datos": facultades_con_datos,
                "fecha_generacion": date.today().strftime("%d/%m/%Y"),
            },
        )
        return generar_pdf_response(html, "quorum_por_facultad.pdf")


class AdherentesPorPropuestaView(SoloAdministradoresMixin, ListView):
    """
    Reporte: Adherentes por propuesta.

    Permite seleccionar una propuesta y mostrar sus adherentes con
    nombre y programa (sin correo electrónico).
    Incluye exportación a PDF.
    """

    model = Adhesion
    template_name = "reportes/adherentes_por_propuesta.html"
    context_object_name = "adhesiones"
    paginate_by = 50

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                "usuario",
                "usuario__programa",
                "propuesta__asignatura",
                "propuesta__periodo",
            )
            .order_by(
                "propuesta__asignatura__nombre",
                "usuario__first_name",
                "usuario__last_name",
            )
        )

        # Filtrar por propuesta si se seleccionó
        propuesta_id = self.request.GET.get("propuesta")
        if propuesta_id:
            queryset = queryset.filter(propuesta_id=propuesta_id)

        # Solo propuestas no rechazadas
        queryset = queryset.exclude(propuesta__estado=Propuesta.Estado.RECHAZADA)

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        # Obtener lista de propuestas para el selector
        propuestas = (
            Propuesta.objects.exclude(estado=Propuesta.Estado.RECHAZADA)
            .select_related("asignatura", "periodo")
            .order_by("asignatura__nombre", "periodo__nombre")
        )

        contexto["propuestas"] = propuestas
        contexto["propuesta_seleccionada"] = self.request.GET.get("propuesta", "")
        contexto["encabezados"] = (
            "Nombre",
            "Programa",
            "Propuesta",
            "Fecha de adhesión",
        )
        contexto["filas"] = self._construir_filas(contexto["adhesiones"])
        contexto["url_crear"] = None  # No hay creación en reportes
        return contexto

    def _construir_filas(self, adhesiones):
        """Construir filas para la tabla: nombre, programa, propuesta y fecha.

        Nunca incluye el correo del adherente (privacidad, Ley 1581 de 2012).
        """
        filas = []
        for adhesion in adhesiones:
            usuario = adhesion.usuario
            nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
            programa = usuario.programa.nombre if usuario.programa_id else "—"
            propuesta_str = f"{adhesion.propuesta.asignatura.nombre} - {adhesion.propuesta.periodo.nombre}"
            fecha_adhesion = adhesion.creada.strftime("%d/%m/%Y %H:%M")
            filas.append([nombre_completo, programa, propuesta_str, fecha_adhesion])
        return filas


class AdherentesPorPropuestaPDFView(SoloAdministradoresMixin, TemplateView):
    """
    Exporta el listado de adherentes por propuesta a PDF usando xhtml2pdf.

    xhtml2pdf es Python puro (basado en ReportLab), por lo que funciona en
    Windows sin instalar librerías nativas como el runtime GTK3 de WeasyPrint.
    """

    template_name = "reportes/adherentes_pdf.html"

    def get(self, request, *args, **kwargs):
        propuesta_id = request.GET.get("propuesta")
        if not propuesta_id:
            return HttpResponse("Debe seleccionar una propuesta", status=400)

        try:
            propuesta = Propuesta.objects.select_related(
                "asignatura",
                "periodo",
                "asignatura__programa",
                "asignatura__programa__facultad",
            ).get(pk=propuesta_id)
        except Propuesta.DoesNotExist:
            return HttpResponse("Propuesta no encontrada", status=404)

        if propuesta.estado == Propuesta.Estado.RECHAZADA:
            return HttpResponse(
                "No se puede generar reporte de propuesta rechazada", status=400
            )

        adhesiones = (
            Adhesion.objects.filter(propuesta=propuesta)
            .select_related("usuario", "usuario__programa")
            .order_by("usuario__first_name", "usuario__last_name")
        )

        # Construir datos para el PDF
        filas = []
        for adhesion in adhesiones:
            usuario = adhesion.usuario
            nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
            programa = usuario.programa.nombre if usuario.programa_id else "—"
            fecha_adhesion = adhesion.creada.strftime("%d/%m/%Y %H:%M")
            filas.append(
                {
                    "nombre": nombre_completo,
                    "programa": programa,
                    "fecha": fecha_adhesion,
                }
            )

        html = render_to_string(
            self.template_name,
            {
                "propuesta": propuesta,
                "filas": filas,
                "total": len(filas),
                "fecha_generacion": date.today().strftime("%d/%m/%Y"),
            },
        )

        # Nombre de archivo corto y seguro: solo código de asignatura y periodo
        periodo_slug = "".join(
            c for c in propuesta.periodo.nombre if c.isalnum() or c in "-_"
        )[:30]
        nombre_archivo = f"adherentes_{propuesta.asignatura.codigo}_{periodo_slug}.pdf"
        return generar_pdf_response(html, nombre_archivo)
