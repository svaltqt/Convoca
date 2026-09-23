import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Docente
from apps.usuarios.models import Usuario


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_anonimo_es_redirigido_a_login_al_listar_docentes(client):
    respuesta = client.get(reverse("academico:docente_lista"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_al_listado_de_docentes(client):
    client.force_login(crear_estudiante())

    respuesta = client.get(reverse("academico:docente_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_administrador_puede_consultar_el_listado_de_docentes(client):
    baker.make(Docente, nombre="Docente de Prueba", disponible=True, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"))

    assert respuesta.status_code == 200
    assert "Docente de Prueba" in respuesta.content.decode()


@pytest.mark.django_db
def test_administrador_puede_buscar_docentes_por_nombre(client):
    baker.make(Docente, nombre="Juan Pérez", disponible=True, activo=True)
    baker.make(Docente, nombre="María González", disponible=True, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"), {"q": "Juan"})
    contenido = respuesta.content.decode()

    assert "Juan Pérez" in contenido
    assert "María González" not in contenido


@pytest.mark.django_db
def test_administrador_puede_buscar_docentes_por_email(client):
    baker.make(Docente, nombre="Juan Pérez", email="juan@elpoli.edu.co", disponible=True, activo=True)
    baker.make(Docente, nombre="María González", email="maria@elpoli.edu.co", disponible=True, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"), {"q": "juan@elpoli"})
    contenido = respuesta.content.decode()

    assert "Juan Pérez" in contenido
    assert "María González" not in contenido


@pytest.mark.django_db
def test_listado_de_docentes_solo_muestra_activos_por_defecto(client):
    baker.make(Docente, nombre="Docente Activo", disponible=True, activo=True)
    baker.make(Docente, nombre="Docente Inactivo", disponible=True, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"))
    contenido = respuesta.content.decode()

    assert "Docente Activo" in contenido
    assert "Docente Inactivo" not in contenido


@pytest.mark.django_db
def test_listado_de_docentes_permite_filtrar_por_inactivos(client):
    baker.make(Docente, nombre="Docente Activo", disponible=True, activo=True)
    baker.make(Docente, nombre="Docente Inactivo", disponible=True, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"), {"estado": "inactivas"})
    contenido = respuesta.content.decode()

    assert "Docente Inactivo" in contenido
    assert "Docente Activo" not in contenido


@pytest.mark.django_db
def test_listado_de_docentes_permite_filtrar_por_todas(client):
    baker.make(Docente, nombre="Docente Activo", disponible=True, activo=True)
    baker.make(Docente, nombre="Docente Inactivo", disponible=True, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"), {"estado": "todas"})
    contenido = respuesta.content.decode()

    assert "Docente Activo" in contenido
    assert "Docente Inactivo" in contenido


@pytest.mark.django_db
def test_listado_ofrece_reactivar_para_un_docente_inactivo(client):
    baker.make(Docente, nombre="Docente Inactivo", disponible=True, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"), {"estado": "todas"})
    contenido = respuesta.content.decode()

    assert "Reactivar" in contenido
    assert "Desactivar" not in contenido


@pytest.mark.django_db
def test_listado_ofrece_desactivar_para_un_docente_activo(client):
    baker.make(Docente, nombre="Docente Activo", disponible=True, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:docente_lista"))
    contenido = respuesta.content.decode()

    assert "Desactivar" in contenido
    assert "Reactivar" not in contenido


@pytest.mark.django_db
def test_administrador_puede_crear_un_docente(client):
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:docente_crear"),
        data={
            "nombre": "Ana López",
            "email": "ana@elpoli.edu.co",
            "disponible": True,
            "activo": True,
        },
    )

    assert respuesta.status_code == 302
    assert Docente.objects.filter(nombre="Ana López", email="ana@elpoli.edu.co").exists()


@pytest.mark.django_db
def test_no_crea_docente_sin_nombre(client):
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:docente_crear"),
        data={
            "nombre": "",
            "email": "test@elpoli.edu.co",
            "disponible": True,
            "activo": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    assert Docente.objects.count() == 0


@pytest.mark.django_db
def test_no_crea_docente_sin_email(client):
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:docente_crear"),
        data={
            "nombre": "Ana López",
            "email": "",
            "disponible": True,
            "activo": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    assert Docente.objects.count() == 0


@pytest.mark.django_db
def test_administrador_puede_modificar_un_docente(client):
    docente = baker.make(Docente, nombre="Nombre viejo", email="viejo@elpoli.edu.co")
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:docente_editar", args=[docente.pk]),
        data={
            "nombre": "Nombre nuevo",
            "email": "nuevo@elpoli.edu.co",
            "disponible": False,
            "activo": True,
        },
    )
    docente.refresh_from_db()

    assert respuesta.status_code == 302
    assert docente.nombre == "Nombre nuevo"
    assert docente.email == "nuevo@elpoli.edu.co"
    assert docente.disponible is False
    assert docente.activo is True


@pytest.mark.django_db
def test_desactivar_docente_no_lo_elimina_fisicamente(client):
    docente = baker.make(Docente, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:docente_desactivar", args=[docente.pk])
    )
    docente.refresh_from_db()

    assert respuesta.status_code == 302
    assert Docente.objects.filter(pk=docente.pk).exists()
    assert docente.activo is False


@pytest.mark.django_db
def test_reactivar_docente_lo_vuelve_a_marcar_como_activo(client):
    docente = baker.make(Docente, activo=False)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("academico:docente_reactivar", args=[docente.pk]))
    docente.refresh_from_db()

    assert respuesta.status_code == 302
    assert docente.activo is True