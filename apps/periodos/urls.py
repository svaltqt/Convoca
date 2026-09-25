from django.urls import path

from . import views

app_name = "periodos"

urlpatterns = [
    path("", views.PeriodoListView.as_view(), name="periodo_lista"),
    path("nueva/", views.PeriodoCreateView.as_view(), name="periodo_crear"),
    path("<int:pk>/editar/", views.PeriodoUpdateView.as_view(), name="periodo_editar"),
    path("<int:pk>/desactivar/", views.PeriodoDesactivarView.as_view(), name="periodo_desactivar"),
    path("<int:pk>/reactivar/", views.PeriodoReactivarView.as_view(), name="periodo_reactivar"),
]