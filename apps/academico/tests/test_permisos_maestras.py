"""
Permisos de las vistas genéricas de maestras (tarea 1.3): ListaConBusquedaView,
DesactivarView y ReactivarView en config/views.py deben otorgar acceso según
la pertenencia al grupo Administrador, no según is_staff.

Se prueban aquí, contra Facultad, porque las cinco maestras heredan de la
misma base en config/views.py; probar la base basta. Cada maestra agrega
solo un test de confirmación (ver test_programa_vistas.py, test_asignatura_vistas.py,
test_docente_vistas.py, test_periodo_vistas.py y test_usuario_vistas.py).
"""

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Facultad
from apps.usuarios.models import Usuario

NOMBRE_GRUPO_ADMINISTRADOR = "Administrador"


def crear_usuario_en_grupo_administrador():
    """Usuario sin is_staff pero miembro del grupo Administrador."""
    usuario = baker.make(Usuario, is_staff=False)
    grupo, _ = Group.objects.get_or_create(name=NOMBRE_GRUPO_ADMINISTRADOR)
    usuario.groups.add(grupo)
    return usuario


def crear_usuario_is_staff_sin_grupo():
    """Usuario con is_staff pero sin pertenencia al grupo Administrador."""
    return baker.make(Usuario, is_staff=True)


@pytest.mark.django_db
def test_usuario_del_grupo_administrador_puede_acceder_al_listado_de_facultades(client):
    client.force_login(crear_usuario_en_grupo_administrador())

    respuesta = client.get(reverse("academico:facultad_lista"))

    assert respuesta.status_code == 200


@pytest.mark.django_db
def test_usuario_que_no_pertenece_al_grupo_administrador_no_puede_acceder_al_listado_de_facultades(client):
    client.force_login(crear_usuario_is_staff_sin_grupo())

    respuesta = client.get(reverse("academico:facultad_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_usuario_del_grupo_administrador_puede_desactivar_una_facultad(client):
    facultad = baker.make(Facultad, activa=True)
    client.force_login(crear_usuario_en_grupo_administrador())

    respuesta = client.post(reverse("academico:facultad_desactivar", args=[facultad.pk]))

    assert respuesta.status_code == 302
    facultad.refresh_from_db()
    assert facultad.activa is False


@pytest.mark.django_db
def test_usuario_que_no_pertenece_al_grupo_administrador_no_puede_desactivar_una_facultad(client):
    facultad = baker.make(Facultad, activa=True)
    client.force_login(crear_usuario_is_staff_sin_grupo())

    respuesta = client.post(reverse("academico:facultad_desactivar", args=[facultad.pk]))

    assert respuesta.status_code == 403
    facultad.refresh_from_db()
    assert facultad.activa is True


@pytest.mark.django_db
def test_usuario_del_grupo_administrador_puede_reactivar_una_facultad(client):
    facultad = baker.make(Facultad, activa=False)
    client.force_login(crear_usuario_en_grupo_administrador())

    respuesta = client.post(reverse("academico:facultad_reactivar", args=[facultad.pk]))

    assert respuesta.status_code == 302
    facultad.refresh_from_db()
    assert facultad.activa is True


@pytest.mark.django_db
def test_usuario_que_no_pertenece_al_grupo_administrador_no_puede_reactivar_una_facultad(client):
    facultad = baker.make(Facultad, activa=False)
    client.force_login(crear_usuario_is_staff_sin_grupo())

    respuesta = client.post(reverse("academico:facultad_reactivar", args=[facultad.pk]))

    assert respuesta.status_code == 403
    facultad.refresh_from_db()
    assert facultad.activa is False
