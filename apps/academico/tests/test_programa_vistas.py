import pytest
from django.contrib.auth.models import Group
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Facultad, Programa
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
def test_anonimo_es_redirigido_a_login_al_listar_programas(client):
    respuesta = client.get(reverse("academico:programa_lista"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_al_listado_de_programas(client):
    client.force_login(crear_estudiante())

    respuesta = client.get(reverse("academico:programa_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_administrador_puede_consultar_el_listado_de_programas(client):
    facultad = baker.make(Facultad, activa=True)
    baker.make(
        Programa, nombre="Ingeniería de Sistemas", facultad=facultad, activo=True
    )
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_lista"))

    assert respuesta.status_code == 200
    assert "Ingeniería de Sistemas" in respuesta.content.decode()


@pytest.mark.django_db
def test_listado_de_programas_muestra_la_facultad_de_cada_programa(client):
    facultad = baker.make(Facultad, nombre="Facultad de Ingenierías", activa=True)
    baker.make(
        Programa, nombre="Ingeniería de Sistemas", facultad=facultad, activo=True
    )
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_lista"))

    assert "Facultad de Ingenierías" in respuesta.content.decode()


@pytest.mark.django_db
def test_administrador_puede_buscar_programas_por_nombre(client):
    facultad = baker.make(Facultad, activa=True)
    baker.make(
        Programa, nombre="Ingeniería de Sistemas", facultad=facultad, activo=True
    )
    baker.make(Programa, nombre="Contaduría Pública", facultad=facultad, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_lista"), {"q": "Sistemas"})
    contenido = respuesta.content.decode()

    assert "Ingeniería de Sistemas" in contenido
    assert "Contaduría Pública" not in contenido


@pytest.mark.django_db
def test_listado_de_programas_solo_muestra_activos_por_defecto(client):
    facultad = baker.make(Facultad, activa=True)
    baker.make(Programa, nombre="Programa Activo", facultad=facultad, activo=True)
    baker.make(Programa, nombre="Programa Inactivo", facultad=facultad, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_lista"))
    contenido = respuesta.content.decode()

    assert "Programa Activo" in contenido
    assert "Programa Inactivo" not in contenido


@pytest.mark.django_db
def test_listado_de_programas_permite_filtrar_por_inactivos(client):
    facultad = baker.make(Facultad, activa=True)
    baker.make(Programa, nombre="Programa Activo", facultad=facultad, activo=True)
    baker.make(Programa, nombre="Programa Inactivo", facultad=facultad, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_lista"), {"estado": "inactivas"})
    contenido = respuesta.content.decode()

    assert "Programa Inactivo" in contenido
    assert "Programa Activo" not in contenido


@pytest.mark.django_db
def test_listado_de_programas_permite_filtrar_por_facultad(client):
    facultad_1 = baker.make(Facultad, nombre="Facultad Uno", activa=True)
    facultad_2 = baker.make(Facultad, nombre="Facultad Dos", activa=True)
    baker.make(Programa, nombre="Programa de la Uno", facultad=facultad_1, activo=True)
    baker.make(Programa, nombre="Programa de la Dos", facultad=facultad_2, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(
        reverse("academico:programa_lista"), {"facultad": facultad_1.pk}
    )
    contenido = respuesta.content.decode()

    assert "Programa de la Uno" in contenido
    assert "Programa de la Dos" not in contenido


@pytest.mark.django_db
def test_administrador_puede_crear_un_programa(client):
    facultad = baker.make(Facultad, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:programa_crear"),
        data={
            "nombre": "Ingeniería de Sistemas",
            "codigo": "ISI",
            "facultad": facultad.pk,
        },
    )

    assert respuesta.status_code == 302
    assert Programa.objects.filter(nombre="Ingeniería de Sistemas").exists()


@pytest.mark.django_db
def test_no_crea_programa_sin_nombre(client):
    facultad = baker.make(Facultad, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:programa_crear"),
        data={"nombre": "", "codigo": "ISI", "facultad": facultad.pk},
    )

    assert respuesta.status_code == 200
    assert Programa.objects.count() == 0


@pytest.mark.django_db
def test_formulario_de_programa_solo_ofrece_facultades_activas(client):
    baker.make(Facultad, nombre="Facultad Activa", activa=True)
    baker.make(Facultad, nombre="Facultad Inactiva", activa=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_crear"))
    contenido = respuesta.content.decode()

    assert "Facultad Activa" in contenido
    assert "Facultad Inactiva" not in contenido


@pytest.mark.django_db
def test_editar_programa_conserva_su_facultad_aunque_este_inactiva(client):
    facultad_inactiva = baker.make(Facultad, nombre="Facultad Inactiva", activa=False)
    programa = baker.make(Programa, facultad=facultad_inactiva, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:programa_editar", args=[programa.pk]))

    assert "Facultad Inactiva" in respuesta.content.decode()


@pytest.mark.django_db
def test_administrador_puede_modificar_un_programa(client):
    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(
        Programa, nombre="Nombre viejo", facultad=facultad, activo=True
    )
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:programa_editar", args=[programa.pk]),
        data={
            "nombre": "Nombre nuevo",
            "codigo": programa.codigo,
            "facultad": facultad.pk,
        },
    )
    programa.refresh_from_db()

    assert respuesta.status_code == 302
    assert programa.nombre == "Nombre nuevo"


@pytest.mark.django_db
def test_desactivar_programa_no_lo_elimina_fisicamente(client):
    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:programa_desactivar", args=[programa.pk])
    )
    programa.refresh_from_db()

    assert respuesta.status_code == 302
    assert Programa.objects.filter(pk=programa.pk).exists()
    assert programa.activo is False


@pytest.mark.django_db
def test_reactivar_programa_lo_vuelve_a_marcar_como_activo(client):
    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("academico:programa_reactivar", args=[programa.pk]))
    programa.refresh_from_db()

    assert respuesta.status_code == 302
    assert programa.activo is True


@pytest.mark.django_db
def test_listado_de_programas_hereda_el_permiso_del_grupo_administrador(client):
    """
    Confirma que ProgramaListView hereda de ListaConBusquedaView la
    verificación de grupo (tarea 1.3) sin reimplementarla: un usuario sin
    is_staff pero miembro del grupo Administrador puede consultar el listado.
    """
    usuario = baker.make(Usuario, is_staff=False)
    grupo, _ = Group.objects.get_or_create(name="Administrador")
    usuario.groups.add(grupo)
    client.force_login(usuario)

    respuesta = client.get(reverse("academico:programa_lista"))

    assert respuesta.status_code == 200
