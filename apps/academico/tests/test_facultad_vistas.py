import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Facultad
from apps.usuarios.models import Usuario


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_anonimo_es_redirigido_a_login_al_listar_facultades(client):
    respuesta = client.get(reverse("academico:facultad_lista"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_al_listado_de_facultades(client):
    client.force_login(crear_estudiante())

    respuesta = client.get(reverse("academico:facultad_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_administrador_puede_consultar_el_listado_de_facultades(client):
    baker.make(Facultad, nombre="Facultad de Ingenierías")
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:facultad_lista"))

    assert respuesta.status_code == 200
    assert "Facultad de Ingenierías" in respuesta.content.decode()


@pytest.mark.django_db
def test_administrador_puede_buscar_facultades_por_nombre(client):
    baker.make(Facultad, nombre="Facultad de Ingenierías")
    baker.make(Facultad, nombre="Facultad de Ciencias Sociales")
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:facultad_lista"), {"q": "Ingenier"})
    contenido = respuesta.content.decode()

    assert "Facultad de Ingenierías" in contenido
    assert "Facultad de Ciencias Sociales" not in contenido


@pytest.mark.django_db
def test_administrador_puede_crear_una_facultad(client):
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:facultad_crear"),
        data={"nombre": "Facultad de Ciencias Sociales"},
    )

    assert respuesta.status_code == 302
    assert Facultad.objects.filter(nombre="Facultad de Ciencias Sociales").exists()


@pytest.mark.django_db
def test_no_crea_facultad_sin_nombre(client):
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("academico:facultad_crear"), data={"nombre": ""})

    assert respuesta.status_code == 200
    assert Facultad.objects.count() == 0


@pytest.mark.django_db
def test_administrador_puede_modificar_una_facultad(client):
    facultad = baker.make(Facultad, nombre="Nombre viejo")
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:facultad_editar", args=[facultad.pk]),
        data={"nombre": "Nombre nuevo"},
    )
    facultad.refresh_from_db()

    assert respuesta.status_code == 302
    assert facultad.nombre == "Nombre nuevo"


@pytest.mark.django_db
def test_desactivar_facultad_no_la_elimina_fisicamente(client):
    facultad = baker.make(Facultad, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("academico:facultad_desactivar", args=[facultad.pk]))
    facultad.refresh_from_db()

    assert respuesta.status_code == 302
    assert Facultad.objects.filter(pk=facultad.pk).exists()
    assert facultad.activa is False
