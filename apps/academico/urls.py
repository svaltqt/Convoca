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
]
