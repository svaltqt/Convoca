"""
Eliminación de cuenta (tarea 1.6, HU-17 criterio 2, reglas 18 y 13 de
CLAUDE.md): las adhesiones a propuestas ABIERTA o QUORUM se eliminan y el
estado de cada propuesta se recalcula igual que en un retiro voluntario,
todo en una sola transacción.

Fuera de este ciclo: propuestas RADICADA o posteriores con anonimización
(criterio 3) y el bloqueo de login (criterio 4).
"""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from apps.academico.models import Asignatura
from apps.periodos.models import Periodo
from apps.propuestas.models import Adhesion, Propuesta
from apps.usuarios.models import Usuario
from apps.usuarios.services import eliminar_cuenta


def crear_estudiante():
    return baker.make(
        Usuario,
        is_staff=False,
        autorizo_datos=True,
        fecha_autorizacion=timezone.now(),
    )


def crear_propuesta(cupo_minimo=20):
    periodo = baker.make(
        Periodo,
        abierto=True,
        cupo_minimo=cupo_minimo,
        fecha_cierre_propuestas=timezone.localdate() + datetime.timedelta(days=10),
    )
    asignatura = baker.make(Asignatura, activa=True)
    return Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=crear_estudiante()
    )


@pytest.mark.django_db
def test_usuario_sin_adhesiones_puede_eliminar_su_cuenta():
    usuario = crear_estudiante()

    eliminar_cuenta(usuario)

    usuario.refresh_from_db()
    assert usuario.is_active is False


@pytest.mark.django_db
def test_eliminar_cuenta_borra_la_adhesion_a_una_propuesta_abierta():
    propuesta = crear_propuesta(cupo_minimo=20)
    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)

    eliminar_cuenta(usuario)

    propuesta.refresh_from_db()
    assert not Adhesion.objects.filter(usuario=usuario).exists()
    assert propuesta.estado == Propuesta.Estado.ABIERTA


@pytest.mark.django_db
def test_eliminar_cuenta_devuelve_a_abierta_una_propuesta_que_queda_bajo_el_cupo():
    propuesta = crear_propuesta(cupo_minimo=2)
    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)
    propuesta.refresh_from_db()
    assert propuesta.estado == Propuesta.Estado.QUORUM

    eliminar_cuenta(usuario)

    propuesta.refresh_from_db()
    assert not Adhesion.objects.filter(usuario=usuario).exists()
    assert propuesta.estado == Propuesta.Estado.ABIERTA


@pytest.mark.django_db
def test_eliminar_cuenta_con_periodo_cerrado_borra_la_adhesion_y_recalcula_el_estado():
    """
    La eliminación de cuenta es un derecho de supresión (Ley 1581), no un
    retiro voluntario: la restricción de periodo abierto (regla 11) no
    aplica aquí.
    """
    propuesta = crear_propuesta(cupo_minimo=2)
    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)
    Periodo.objects.filter(pk=propuesta.periodo_id).update(abierto=False)
    propuesta.refresh_from_db()
    assert propuesta.estado == Propuesta.Estado.QUORUM

    eliminar_cuenta(usuario)

    propuesta.refresh_from_db()
    usuario.refresh_from_db()
    assert not Adhesion.objects.filter(usuario=usuario).exists()
    assert propuesta.estado == Propuesta.Estado.ABIERTA
    assert usuario.is_active is False


@pytest.mark.django_db
def test_eliminar_cuenta_revierte_todo_si_falla_a_mitad_de_la_transaccion(monkeypatch):
    propuesta = crear_propuesta(cupo_minimo=2)
    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)

    def fallar(*args, **kwargs):
        raise RuntimeError("fallo simulado al desactivar la cuenta")

    monkeypatch.setattr(Usuario, "save", fallar)

    with pytest.raises(RuntimeError):
        eliminar_cuenta(usuario)

    propuesta.refresh_from_db()
    assert Adhesion.objects.filter(usuario=usuario).exists()
    assert propuesta.estado == Propuesta.Estado.QUORUM


@pytest.mark.django_db
def test_la_pantalla_de_confirmacion_no_elimina_la_cuenta_por_si_sola(client):
    usuario = crear_estudiante()
    client.force_login(usuario)

    respuesta = client.get(reverse("usuarios:eliminar_cuenta"))

    usuario.refresh_from_db()
    assert respuesta.status_code == 200
    assert usuario.is_active is True


@pytest.mark.django_db
def test_usuario_confirma_la_eliminacion_y_se_cierra_su_sesion(client):
    usuario = crear_estudiante()
    client.force_login(usuario)

    respuesta = client.post(reverse("usuarios:eliminar_cuenta"))

    usuario.refresh_from_db()
    assert respuesta.status_code == 302
    assert usuario.is_active is False
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_cuenta_eliminada_no_puede_volver_a_iniciar_sesion(client):
    """
    Regresión del criterio 4 de HU-17 (regla 20). No requirió código nuevo:
    eliminar_cuenta() deja is_active=False y el ModelBackend de Django
    rechaza la autenticación de cuentas inactivas.
    """
    usuario = Usuario.objects.create_user(
        email="ana@elpoli.edu.co", password="ClaveDePrueba2026"
    )
    eliminar_cuenta(usuario)

    respuesta = client.post(
        reverse("usuarios:entrar"),
        data={"username": "ana@elpoli.edu.co", "password": "ClaveDePrueba2026"},
    )

    assert respuesta.status_code == 200
    assert "_auth_user_id" not in client.session
