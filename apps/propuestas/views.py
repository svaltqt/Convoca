from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import format_html
from django.views.generic import CreateView, DetailView, ListView, View
from django.views.generic.base import TemplateResponseMixin

from config.views import SoloAdministradoresMixin
from .forms import PropuestaForm
from .models import Adhesion, Propuesta, TransicionInvalidaError


class PropuestaListView(LoginRequiredMixin, ListView):
    """Listado de propuestas accesible para estudiantes y administradores."""
    model = Propuesta
    template_name = "propuestas/propuesta_lista.html"
    context_object_name = "propuestas"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar solo propuestas activas (no rechazadas) para la vista de listado
        # según las reglas de negocio: se considera activa toda propuesta en cualquier estado distinto de RECHAZADA
        queryset = queryset.exclude(estado=Propuesta.Estado.RECHAZADA)

        # Búsqueda por nombre de asignatura o periodo
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            queryset = queryset.filter(
                Q(asignatura__nombre__icontains=busqueda) |
                Q(periodo__nombre__icontains=busqueda)
            )

        return queryset.select_related("asignatura", "periodo", "creador").order_by("-creada")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update({
            "url_crear": reverse("propuestas:propuesta_crear"),
            "texto_crear": "Nueva propuesta",
            "busqueda": self.request.GET.get("q", ""),
            "estado": None,
            "encabezados": ("Asignatura", "Periodo", "Interesados", "Estado", "Acciones"),
            "filas": [[
                format_html('<a href="{}">{}</a>', reverse("propuestas:propuesta_detalle", args=[p.pk]), p.asignatura.nombre),
                p.periodo.nombre, p.total_adhesiones, p.get_estado_display(),
            ] for p in contexto["propuestas"]],
        })
        return contexto


class PropuestaCreateView(LoginRequiredMixin, CreateView):
    """Creación de propuesta: solo estudiantes pueden crear propuestas."""
    model = Propuesta
    form_class = PropuestaForm
    template_name = "propuestas/propuesta_formulario.html"
    success_url = reverse_lazy("propuestas:propuesta_lista")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            messages.warning(request, "La creación de propuestas está disponible para estudiantes.")
            return redirect("propuestas:propuesta_lista")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Asignar el creador como el usuario actual
        form.instance.creador = self.request.user
        try:
            with transaction.atomic():
                respuesta = super().form_valid(form)
                messages.success(
                    self.request,
                    f'Se creó la propuesta «{self.object.asignatura} - {self.object.periodo}».'
                )
                return respuesta
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except IntegrityError:
            form.add_error(None, "Ya existe una propuesta activa para esta asignatura y periodo.")
            return self.form_invalid(form)


class PropuestaDetalleView(LoginRequiredMixin, DetailView):
    """Detalle de propuesta: accesible para usuarios autenticados."""
    model = Propuesta
    template_name = "propuestas/propuesta_detalle.html"
    context_object_name = "propuesta"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        propuesta = self.get_object()

        # Verificar si el usuario actual ya está adherido
        usuario = self.request.user
        contexto["ya_adherido"] = propuesta.adhesiones.filter(usuario=usuario).exists()
        contexto["faltan_para_quorum"] = max(
            propuesta.periodo.cupo_minimo - propuesta.total_adhesiones,
            0,
        )
        cupo_minimo = max(propuesta.periodo.cupo_minimo, 1)
        contexto["porcentaje_quorum"] = min(
            int(propuesta.total_adhesiones * 100 / cupo_minimo),
            100,
        )

        # Verificar si el usuario puede adherirse (para mostrar el botón)
        contexto["puede_adherirse"] = (
            not contexto["ya_adherido"] and
            propuesta.periodo.abierto and
            propuesta.periodo.fecha_cierre_propuestas >= timezone.now().date() and
            usuario.autorizo_datos and
            propuesta.estado in [Propuesta.Estado.ABIERTA, Propuesta.Estado.QUORUM]
        )

        # Verificar si el usuario puede retirar su adhesión
        contexto["puede_retirar"] = (
            contexto["ya_adherido"] and
            propuesta.periodo.abierto and
            propuesta.estado in [Propuesta.Estado.ABIERTA, Propuesta.Estado.QUORUM]
        )

        # Para administradores, mostrar opciones de cambio de estado
        contexto["es_administrador"] = usuario.is_staff
        contexto["fecha_vencida"] = propuesta.periodo.fecha_cierre_propuestas < timezone.localdate()

        return contexto


class PropuestaEstadoView(SoloAdministradoresMixin, View):
    """Cambio de estado de propuesta: solo administradores."""

    def post(self, request, pk, estado=None):
        propuesta = get_object_or_404(Propuesta, pk=pk)
        nuevo_estado = estado or request.POST.get("estado")

        # Validar que el estado sea válido
        if nuevo_estado not in dict(Propuesta.Estado.choices):
            messages.error(request, "Estado no válido.")
            return redirect("propuestas:propuesta_detalle", pk=propuesta.pk)

        # Verificar transiciones permitidas según las reglas de negocio
        try:
            with transaction.atomic():
                propuesta = Propuesta.objects.select_for_update().get(pk=pk)
                propuesta.cambiar_estado(nuevo_estado)
            messages.success(request, f"Propuesta cambiada a {propuesta.get_estado_display()}.")
        except TransicionInvalidaError as e:
            messages.error(request, str(e))

        return redirect("propuestas:propuesta_detalle", pk=propuesta.pk)


class PropuestaAdhesionView(LoginRequiredMixin, View):
    """Adhesión a propuesta: solo estudiantes autorizados."""

    def post(self, request, pk):
        propuesta = get_object_or_404(Propuesta, pk=pk)
        usuario = request.user

        # Solo estudiantes pueden adherirse (no administradores)
        if usuario.is_staff:
            messages.error(request, "Los administradores no pueden adherirse a propuestas.")
            return redirect("propuestas:propuesta_detalle", pk=propuesta.pk)

        try:
            with transaction.atomic():
                # Usar select_for_update para evitar condiciones de carrera
                propuesta = Propuesta.objects.select_for_update().get(pk=propuesta.pk)

                # Crear la adhesión (las validaciones están en el modelo)
                adhesion = Adhesion.objects.create(
                    propuesta=propuesta,
                    usuario=usuario
                )

                messages.success(request, f'Te has adherido correctamente a la propuesta «{propuesta.asignatura} - {propuesta.periodo}».')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "No se pudo procesar la adhesión. Inténtalo nuevamente.")

        return redirect("propuestas:propuesta_detalle", pk=propuesta.pk)


class PropuestaRetiroView(LoginRequiredMixin, View):
    """Retiro de adhesión: solo estudiantes."""

    def post(self, request, pk):
        propuesta = get_object_or_404(Propuesta, pk=pk)
        usuario = request.user

        try:
            with transaction.atomic():
                # Usar select_for_update para evitar condiciones de carrera
                propuesta = Propuesta.objects.select_for_update().get(pk=propuesta.pk)

                if propuesta.estado not in (Propuesta.Estado.ABIERTA, Propuesta.Estado.QUORUM):
                    raise ValidationError("No se puede retirar una adhesión de una propuesta radicada o posterior.")
                if not propuesta.periodo.abierto:
                    raise ValidationError("No se puede retirar una adhesión si el periodo está cerrado.")
                adhesion = Adhesion.objects.filter(propuesta=propuesta, usuario=usuario).first()
                if adhesion:
                    adhesion.delete()
                    messages.success(request, f'Has retirado tu adhesión de la propuesta «{propuesta.asignatura} - {propuesta.periodo}».')
                else:
                    messages.error(request, "No estabas adherido a esta propuesta.")

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "No se pudo procesar el retiro. Inténtalo nuevamente.")

        return redirect("propuestas:propuesta_detalle", pk=propuesta.pk)


class PropuestaAdherentesView(LoginRequiredMixin, ListView):
    """Listado de adherentes de una propuesta: solo usuarios autenticados."""
    model = Adhesion
    template_name = "propuestas/propuesta_adherentes.html"
    context_object_name = "adhesiones"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        # Verificar que la propuesta exista
        self.propuesta = get_object_or_404(Propuesta, pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(
            propuesta=self.propuesta
        ).select_related(
            "usuario", "usuario__programa"
        ).order_by("-creada")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["propuesta"] = self.propuesta
        contexto["ocultar_email_usuario"] = True
        contexto["encabezados"] = ("Nombre", "Programa")
        contexto["filas"] = [[
            f"{a.usuario.first_name} {a.usuario.last_name}".strip(),
            a.usuario.programa.nombre if a.usuario.programa_id else "—",
        ] for a in contexto["adhesiones"]]
        return contexto
