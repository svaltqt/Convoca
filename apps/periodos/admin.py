from django.contrib import admin

from .models import Periodo


@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "inicio",
        "fin",
        "fecha_cierre_propuestas",
        "cupo_minimo",
        "abierto",
    )
    list_filter = ("abierto",)
    search_fields = ("nombre",)
