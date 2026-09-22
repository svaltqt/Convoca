from django.contrib import admin

from .models import Adhesion, Propuesta


@admin.register(Propuesta)
class PropuestaAdmin(admin.ModelAdmin):
    list_display = ("asignatura", "periodo", "creador", "docente", "estado", "creada")
    list_filter = ("estado", "periodo", "docente")
    search_fields = (
        "asignatura__nombre",
        "asignatura__codigo",
        "creador__email",
    )


@admin.register(Adhesion)
class AdhesionAdmin(admin.ModelAdmin):
    list_display = ("propuesta", "usuario", "creada")
    list_filter = ("propuesta__periodo", "propuesta__estado")
    search_fields = (
        "usuario__email",
        "propuesta__asignatura__nombre",
    )
