from django.urls import path

from . import views

app_name = "reportes"

urlpatterns = [
    path("", views.ReportesIndexView.as_view(), name="index"),
    path(
        "quorum-por-facultad/",
        views.QuorumPorFacultadView.as_view(),
        name="quorum_por_facultad",
    ),
    path(
        "quorum-por-facultad/pdf/",
        views.QuorumPorFacultadPDFView.as_view(),
        name="quorum_por_facultad_pdf",
    ),
    path(
        "adherentes-por-propuesta/",
        views.AdherentesPorPropuestaView.as_view(),
        name="adherentes_por_propuesta",
    ),
    path(
        "adherentes-por-propuesta/pdf/",
        views.AdherentesPorPropuestaPDFView.as_view(),
        name="adherentes_por_propuesta_pdf",
    ),
]
