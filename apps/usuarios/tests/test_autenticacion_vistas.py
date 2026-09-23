import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Programa
from apps.usuarios.models import Usuario


def crear_programa_activo():
    return baker.make(Programa, activo=True)


@pytest.mark.django_db
def test_login_con_credenciales_validas_redirige_a_inicio(client):
    Usuario.objects.create_user(email="ana@elpoli.edu.co", password="ClaveSegura2026")

    respuesta = client.post(
        reverse("usuarios:entrar"),
        {"username": "ana@elpoli.edu.co", "password": "ClaveSegura2026"},
    )

    assert respuesta.status_code == 302
    assert respuesta.url == reverse("inicio")


@pytest.mark.django_db
def test_login_con_credenciales_invalidas_muestra_error(client):
    Usuario.objects.create_user(email="ana@elpoli.edu.co", password="ClaveSegura2026")

    respuesta = client.post(
        reverse("usuarios:entrar"),
        {"username": "ana@elpoli.edu.co", "password": "clave-incorrecta"},
    )

    assert respuesta.status_code == 200
    assert "Correo o contraseña incorrectos" in respuesta.content.decode()
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_cerrar_sesion_termina_la_sesion_del_usuario(client):
    Usuario.objects.create_user(email="ana@elpoli.edu.co", password="ClaveSegura2026")
    client.login(username="ana@elpoli.edu.co", password="ClaveSegura2026")
    assert "_auth_user_id" in client.session

    respuesta = client.post(reverse("usuarios:salir"))

    assert respuesta.status_code == 302
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_registro_exitoso_crea_el_usuario(client):
    programa = crear_programa_activo()

    respuesta = client.post(
        reverse("usuarios:registro"),
        {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana.gomez@elpoli.edu.co",
            "programa": programa.pk,
            "password": "ClaveSegura2026",
            "autorizo_datos": "on",
        },
    )

    assert respuesta.status_code == 302
    assert Usuario.objects.filter(email="ana.gomez@elpoli.edu.co").exists()


@pytest.mark.django_db
def test_registro_rechaza_correo_fuera_del_dominio_institucional(client):
    programa = crear_programa_activo()

    respuesta = client.post(
        reverse("usuarios:registro"),
        {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana.gomez@gmail.com",
            "programa": programa.pk,
            "password": "ClaveSegura2026",
            "autorizo_datos": "on",
        },
    )

    assert respuesta.status_code == 200
    assert not Usuario.objects.filter(email="ana.gomez@gmail.com").exists()
    assert "dominio institucional" in respuesta.content.decode()


@pytest.mark.django_db
def test_registro_rechaza_sin_autorizacion_de_datos(client):
    programa = crear_programa_activo()

    respuesta = client.post(
        reverse("usuarios:registro"),
        {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana.gomez@elpoli.edu.co",
            "programa": programa.pk,
            "password": "ClaveSegura2026",
        },
    )

    assert respuesta.status_code == 200
    assert not Usuario.objects.filter(email="ana.gomez@elpoli.edu.co").exists()


@pytest.mark.django_db
def test_registro_sin_autorizacion_muestra_mensaje_especifico(client):
    programa = crear_programa_activo()

    respuesta = client.post(
        reverse("usuarios:registro"),
        {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana.gomez@elpoli.edu.co",
            "programa": programa.pk,
            "password": "ClaveSegura2026",
        },
    )

    assert (
        "Debe autorizar el tratamiento de sus datos personales para crear la cuenta."
        in respuesta.content.decode()
    )


@pytest.mark.django_db
def test_registro_guarda_la_fecha_de_autorizacion(client):
    programa = crear_programa_activo()

    client.post(
        reverse("usuarios:registro"),
        {
            "first_name": "Ana",
            "last_name": "Gómez",
            "email": "ana.gomez@elpoli.edu.co",
            "programa": programa.pk,
            "password": "ClaveSegura2026",
            "autorizo_datos": "on",
        },
    )

    usuario = Usuario.objects.get(email="ana.gomez@elpoli.edu.co")
    assert usuario.fecha_autorizacion is not None


@pytest.mark.django_db
def test_registro_solo_ofrece_programas_activos_en_el_desplegable(client):
    activo = baker.make(Programa, nombre="Programa Activo", activo=True)
    baker.make(Programa, nombre="Programa Inactivo", activo=False)

    respuesta = client.get(reverse("usuarios:registro"))
    contenido = respuesta.content.decode()

    assert "Programa Activo" in contenido
    assert "Programa Inactivo" not in contenido
    assert activo.pk is not None
