"""
Pantalla de perfil (tarea 1.6, primer criterio de HU-17): un usuario
autenticado puede ver y editar su propio perfil (nombre, apellido,
programa), pero no su correo institucional ni su autorización de
tratamiento de datos. La eliminación de cuenta es un criterio aparte, que
no se implementa aquí.
"""

import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Programa
from apps.usuarios.models import Usuario


@pytest.mark.django_db
def test_anonimo_es_redirigido_a_login_al_ver_el_perfil(client):
    respuesta = client.get(reverse("usuarios:perfil"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_usuario_autenticado_puede_ver_su_perfil_con_sus_datos_actuales(client):
    programa = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    usuario = baker.make(
        Usuario,
        first_name="Ana",
        last_name="Gómez",
        email="ana.gomez@elpoli.edu.co",
        programa=programa,
    )
    client.force_login(usuario)

    respuesta = client.get(reverse("usuarios:perfil"))
    contenido = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert "Ana" in contenido
    assert "Gómez" in contenido
    assert "ana.gomez@elpoli.edu.co" in contenido
    assert "Ingeniería de Sistemas" in contenido


@pytest.mark.django_db
def test_usuario_autenticado_puede_editar_su_perfil(client):
    programa_nuevo = baker.make(Programa, nombre="Programa Nuevo", activo=True)
    usuario = baker.make(
        Usuario, first_name="Ana", last_name="Gómez", email="ana@elpoli.edu.co"
    )
    client.force_login(usuario)

    respuesta = client.post(
        reverse("usuarios:perfil"),
        data={
            "first_name": "Ana María",
            "last_name": "Gómez Ríos",
            "programa": programa_nuevo.pk,
        },
    )

    usuario.refresh_from_db()
    assert respuesta.status_code == 302
    assert usuario.first_name == "Ana María"
    assert usuario.last_name == "Gómez Ríos"
    assert usuario.programa_id == programa_nuevo.pk


@pytest.mark.django_db
def test_usuario_no_puede_editar_su_correo_ni_su_autorizacion_desde_el_perfil(client):
    usuario = baker.make(
        Usuario,
        email="ana@elpoli.edu.co",
        autorizo_datos=True,
    )
    client.force_login(usuario)

    respuesta = client.post(
        reverse("usuarios:perfil"),
        data={
            "first_name": usuario.first_name,
            "last_name": usuario.last_name,
            "programa": "",
            "email": "otro@elpoli.edu.co",
            "autorizo_datos": "",
        },
    )

    usuario.refresh_from_db()
    assert respuesta.status_code == 302
    assert usuario.email == "ana@elpoli.edu.co"
    assert usuario.autorizo_datos is True


@pytest.mark.django_db
def test_el_formulario_de_perfil_no_expone_el_correo_ni_la_autorizacion_como_campos_editables(client):
    usuario = baker.make(Usuario, email="ana@elpoli.edu.co", autorizo_datos=True)
    client.force_login(usuario)

    respuesta = client.get(reverse("usuarios:perfil"))
    contenido = respuesta.content.decode()

    assert 'name="email"' not in contenido
    assert 'name="autorizo_datos"' not in contenido
