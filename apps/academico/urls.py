from django.urls import path

from . import views

app_name = "academico"

urlpatterns = [
    path("facultades/", views.FacultadListView.as_view(), name="facultad_lista"),
    path(
        "facultades/nueva/", views.FacultadCreateView.as_view(), name="facultad_crear"
    ),
    path(
        "facultades/<int:pk>/editar/",
        views.FacultadUpdateView.as_view(),
        name="facultad_editar",
    ),
    path(
        "facultades/<int:pk>/desactivar/",
        views.FacultadDesactivarView.as_view(),
        name="facultad_desactivar",
    ),
    path(
        "facultades/<int:pk>/reactivar/",
        views.FacultadReactivarView.as_view(),
        name="facultad_reactivar",
    ),
    path("programas/", views.ProgramaListView.as_view(), name="programa_lista"),
    path("programas/nuevo/", views.ProgramaCreateView.as_view(), name="programa_crear"),
    path(
        "programas/<int:pk>/editar/",
        views.ProgramaUpdateView.as_view(),
        name="programa_editar",
    ),
    path(
        "programas/<int:pk>/desactivar/",
        views.ProgramaDesactivarView.as_view(),
        name="programa_desactivar",
    ),
    path(
        "programas/<int:pk>/reactivar/",
        views.ProgramaReactivarView.as_view(),
        name="programa_reactivar",
    ),
    path("docentes/", views.DocenteListView.as_view(), name="docente_lista"),
    path(
        "docentes/nuevo/", views.DocenteCreateView.as_view(), name="docente_crear"
    ),
    path(
        "docentes/<int:pk>/editar/",
        views.DocenteUpdateView.as_view(),
        name="docente_editar",
    ),
    path(
        "docentes/<int:pk>/desactivar/",
        views.DocenteDesactivarView.as_view(),
        name="docente_desactivar",
    ),
    path(
        "docentes/<int:pk>/reactivar/",
        views.DocenteReactivarView.as_view(),
        name="docente_reactivar",
    ),
    path("asignaturas/", views.AsignaturaListView.as_view(), name="asignatura_lista"),
    path(
        "asignaturas/nueva/", views.AsignaturaCreateView.as_view(), name="asignatura_crear"
    ),
    path(
        "asignaturas/<int:pk>/editar/",
        views.AsignaturaUpdateView.as_view(),
        name="asignatura_editar",
    ),
    path(
        "asignaturas/<int:pk>/desactivar/",
        views.AsignaturaDesactivarView.as_view(),
        name="asignatura_desactivar",
    ),
    path(
        "asignaturas/<int:pk>/reactivar/",
        views.AsignaturaReactivarView.as_view(),
        name="asignatura_reactivar",
    ),
]
