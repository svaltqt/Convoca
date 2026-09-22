from django.contrib import admin

from .models import Asignatura, Docente, Facultad, Programa


@admin.register(Facultad)
class FacultadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre",)


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "facultad", "activo")
    list_filter = ("facultad", "activo")
    search_fields = ("nombre", "codigo")


@admin.register(Asignatura)
class AsignaturaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "programa", "creditos", "activa")
    list_filter = ("programa", "activa")
    search_fields = ("codigo", "nombre")


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "email", "disponible", "activo")
    list_filter = ("disponible", "activo")
    search_fields = ("nombre", "email")
