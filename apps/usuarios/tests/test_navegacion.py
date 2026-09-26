"""
Visibilidad del menú según rol (tarea 1.4): el menú (barra de navegación y
los módulos de administración en la página de inicio) debe mostrar las
opciones de administrador (maestras y reportes) solo a los usuarios del
grupo Administrador, no según is_staff.

Esto es solo sobre visibilidad de enlaces; el acceso real a esas vistas ya
se resolvió en la tarea 1.3 (maestras, config/views.py) y en apps/reportes
(SoloAdministradoresMixin), y no se modifica aquí.
"""

import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from model_bakery import baker

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
def test_usuario_del_grupo_administrador_ve_las_opciones_de_administrador_en_el_menu(client):
    client.force_login(crear_usuario_en_grupo_administrador())

    respuesta = client.get(reverse("inicio"))
    contenido = respuesta.content.decode()

    assert "Facultades" in contenido
    assert "Programas" in contenido
    assert "Asignaturas" in contenido
    assert "Docentes" in contenido
    assert "Periodos" in contenido
    assert "Usuarios" in contenido
    assert "Reportes" in contenido


@pytest.mark.django_db
def test_usuario_que_no_pertenece_al_grupo_administrador_no_ve_las_opciones_de_administrador_en_el_menu(client):
    client.force_login(crear_usuario_is_staff_sin_grupo())

    respuesta = client.get(reverse("inicio"))
    contenido = respuesta.content.decode()

    assert "Facultades" not in contenido
    assert "Reportes" not in contenido
