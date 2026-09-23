from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("entrar/", views.EntrarView.as_view(), name="entrar"),
    path("salir/", views.SalirView.as_view(), name="salir"),
    path("registro/", views.RegistroView.as_view(), name="registro"),
    path("politica-datos/", views.PoliticaDatosView.as_view(), name="politica_datos"),
]
