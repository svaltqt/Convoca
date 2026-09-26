import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Programa
from apps.usuarios.models import Usuario


def crear_administrador():
    """
    Administrador de prueba: is_staff (para las vistas que aún dependen de
    él) y miembro del grupo Administrador (para las vistas genéricas de
    maestras, que a partir de la tarea 1.3 verifican pertenencia al grupo).
    """
    usuario = Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )
    grupo, _ = Group.objects.get_or_create(name="Administrador")
    usuario.groups.add(grupo)
    return usuario


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_anonimo_es_redirigido_a_login_al_listar_usuarios(client):
    respuesta = client.get(reverse("usuarios:usuario_lista"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_al_listado_de_usuarios(client):
    client.force_login(crear_estudiante())

    respuesta = client.get(reverse("usuarios:usuario_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_administrador_puede_consultar_el_listado_de_usuarios(client):
    programa = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    baker.make(
        Usuario,
        first_name="Ana",
        last_name="Gómez",
        email="ana.gomez@elpoli.edu.co",
        programa=programa,
        autorizo_datos=True,
        is_active=True,
    )
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"))
    contenido = respuesta.content.decode()

    assert respuesta.status_code == 200
    assert "Ana" in contenido and "Gómez" in contenido
    assert "ana.gomez@elpoli.edu.co" in contenido
    assert "Ingeniería de Sistemas" in contenido


@pytest.mark.django_db
def test_administrador_puede_buscar_usuarios_por_nombre(client):
    baker.make(Usuario, first_name="Ana", last_name="Gómez", email="ana@elpoli.edu.co")
    baker.make(Usuario, first_name="Luis", last_name="Rojas", email="luis@elpoli.edu.co")
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"), {"q": "Ana"})
    contenido = respuesta.content.decode()

    assert "ana@elpoli.edu.co" in contenido
    assert "luis@elpoli.edu.co" not in contenido


@pytest.mark.django_db
def test_administrador_puede_buscar_usuarios_por_correo(client):
    baker.make(Usuario, first_name="Ana", last_name="Gómez", email="ana@elpoli.edu.co")
    baker.make(Usuario, first_name="Luis", last_name="Rojas", email="luis@elpoli.edu.co")
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"), {"q": "luis@"})
    contenido = respuesta.content.decode()

    assert "luis@elpoli.edu.co" in contenido
    assert "ana@elpoli.edu.co" not in contenido


@pytest.mark.django_db
def test_listado_de_usuarios_solo_muestra_activos_por_defecto(client):
    baker.make(Usuario, email="primera@elpoli.edu.co", is_active=True)
    baker.make(Usuario, email="segunda@elpoli.edu.co", is_active=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"))
    contenido = respuesta.content.decode()

    assert "primera@elpoli.edu.co" in contenido
    assert "segunda@elpoli.edu.co" not in contenido


@pytest.mark.django_db
def test_listado_de_usuarios_permite_filtrar_por_inactivos(client):
    baker.make(Usuario, email="primera@elpoli.edu.co", is_active=True)
    baker.make(Usuario, email="segunda@elpoli.edu.co", is_active=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"), {"estado": "inactivas"})
    contenido = respuesta.content.decode()

    assert "segunda@elpoli.edu.co" in contenido
    assert "primera@elpoli.edu.co" not in contenido


@pytest.mark.django_db
def test_listado_de_usuarios_permite_filtrar_por_programa(client):
    programa_1 = baker.make(Programa, nombre="Programa Uno", activo=True)
    programa_2 = baker.make(Programa, nombre="Programa Dos", activo=True)
    baker.make(Usuario, email="uno@elpoli.edu.co", programa=programa_1)
    baker.make(Usuario, email="dos@elpoli.edu.co", programa=programa_2)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"), {"programa": programa_1.pk})
    contenido = respuesta.content.decode()

    assert "uno@elpoli.edu.co" in contenido
    assert "dos@elpoli.edu.co" not in contenido


@pytest.mark.django_db
def test_administrador_puede_modificar_el_programa_de_un_usuario(client):
    programa_nuevo = baker.make(Programa, nombre="Programa Nuevo", activo=True)
    usuario = baker.make(
        Usuario, first_name="Ana", last_name="Gómez", email="ana@elpoli.edu.co"
    )
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("usuarios:usuario_editar", args=[usuario.pk]),
        data={
            "first_name": "Ana",
            "last_name": "Gómez Ríos",
            "programa": programa_nuevo.pk,
        },
    )
    usuario.refresh_from_db()

    assert respuesta.status_code == 302
    assert usuario.last_name == "Gómez Ríos"
    assert usuario.programa_id == programa_nuevo.pk


@pytest.mark.django_db
def test_desactivar_usuario_no_lo_elimina_fisicamente(client):
    usuario = baker.make(Usuario, email="ana@elpoli.edu.co", is_active=True)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("usuarios:usuario_desactivar", args=[usuario.pk]))
    usuario.refresh_from_db()

    assert respuesta.status_code == 302
    assert Usuario.objects.filter(pk=usuario.pk).exists()
    assert usuario.is_active is False


@pytest.mark.django_db
def test_reactivar_usuario_lo_vuelve_a_marcar_como_activo(client):
    usuario = baker.make(Usuario, email="ana@elpoli.edu.co", is_active=False)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("usuarios:usuario_reactivar", args=[usuario.pk]))
    usuario.refresh_from_db()

    assert respuesta.status_code == 302
    assert usuario.is_active is True


@pytest.mark.django_db
def test_no_hay_boton_de_crear_usuario_en_el_listado(client):
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("usuarios:usuario_lista"))
    contenido = respuesta.content.decode()

    assert "Nuevo usuario" not in contenido
    assert 'href="/usuarios/nuevo/"' not in contenido


@pytest.mark.django_db
def test_contrasena_no_aparece_en_listado_ni_en_formulario_de_edicion(client):
    usuario = Usuario.objects.create_user(
        email="ana@elpoli.edu.co", password="ClaveSuperSecreta2026"
    )
    client.force_login(crear_administrador())

    respuesta_lista = client.get(reverse("usuarios:usuario_lista"))
    respuesta_editar = client.get(reverse("usuarios:usuario_editar", args=[usuario.pk]))

    for respuesta in (respuesta_lista, respuesta_editar):
        contenido = respuesta.content.decode()
        assert "ClaveSuperSecreta2026" not in contenido
        assert usuario.password not in contenido
        assert 'type="password"' not in contenido


@pytest.mark.django_db
def test_listado_de_usuarios_hereda_el_permiso_del_grupo_administrador(client):
    """
    Confirma que UsuarioListView hereda de ListaConBusquedaView la
    verificación de grupo (tarea 1.3) sin reimplementarla: un usuario sin
    is_staff pero miembro del grupo Administrador puede consultar el listado.
    """
    usuario = baker.make(Usuario, is_staff=False)
    grupo, _ = Group.objects.get_or_create(name="Administrador")
    usuario.groups.add(grupo)
    client.force_login(usuario)

    respuesta = client.get(reverse("usuarios:usuario_lista"))

    assert respuesta.status_code == 200
