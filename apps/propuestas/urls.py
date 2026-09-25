from django.urls import path

from . import views

app_name = "propuestas"

urlpatterns = [
    path("", views.PropuestaListView.as_view(), name="propuesta_lista"),
    path("nueva/", views.PropuestaCreateView.as_view(), name="propuesta_crear"),
    path("<int:pk>/", views.PropuestaDetalleView.as_view(), name="propuesta_detalle"),
    path("<int:pk>/estado/", views.PropuestaEstadoView.as_view(), name="propuesta_estado"),
    path("<int:pk>/estado/<str:estado>/", views.PropuestaEstadoView.as_view(), name="propuesta_estado"),
    path("<int:pk>/adhesion/", views.PropuestaAdhesionView.as_view(), name="propuesta_adhesion"),
    path("<int:pk>/retiro/", views.PropuestaRetiroView.as_view(), name="propuesta_retiro"),
    path("<int:pk>/adherentes/", views.PropuestaAdherentesView.as_view(), name="propuesta_adherentes"),
]
