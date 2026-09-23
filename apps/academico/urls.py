from django.urls import path

from . import views

app_name = "academico"

urlpatterns = [
    path("facultades/", views.FacultadListView.as_view(), name="facultad_lista"),
    path("facultades/nueva/", views.FacultadCreateView.as_view(), name="facultad_crear"),
    path("facultades/<int:pk>/editar/", views.FacultadUpdateView.as_view(), name="facultad_editar"),
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
]
