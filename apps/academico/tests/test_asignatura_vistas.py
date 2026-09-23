import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Asignatura, Programa
from apps.usuarios.models import Usuario


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_anonimo_es_redirigido_a_login_al_listar_asignaturas(client):
    respuesta = client.get(reverse("academico:asignatura_lista"))

    assert respuesta.status_code == 302


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_al_listado_de_asignaturas(client):
    client.force_login(crear_estudiante())

    respuesta = client.get(reverse("academico:asignatura_lista"))

    assert respuesta.status_code == 403


@pytest.mark.django_db
def test_administrador_puede_consultar_el_listado_de_asignaturas(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura de Prueba", programa=programa, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"))

    assert respuesta.status_code == 200
    assert "Asignatura de Prueba" in respuesta.content.decode()


@pytest.mark.django_db
def test_administrador_puede_buscar_asignaturas_por_nombre(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Matemáticas I", programa=programa, activa=True)
    baker.make(Asignatura, nombre="Física I", programa=programa, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"), {"q": "Matem"})
    contenido = respuesta.content.decode()

    assert "Matemáticas I" in contenido
    assert "Física I" not in contenido


@pytest.mark.django_db
def test_administrador_puede_buscar_asignaturas_por_codigo(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Cálculo", programa=programa, codigo="MAT101", activa=True)
    baker.make(Asignatura, nombre="Álgebra", programa=programa, codigo="MAT102", activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"), {"q": "MAT101"})
    contenido = respuesta.content.decode()

    assert "Cálculo" in contenido
    assert "Álgebra" not in contenido


@pytest.mark.django_db
def test_listado_de_asignaturas_solo_muestra_activas_por_defecto(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura Activa", programa=programa, activa=True)
    baker.make(Asignatura, nombre="Asignatura Inactiva", programa=programa, activa=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"))
    contenido = respuesta.content.decode()

    assert "Asignatura Activa" in contenido
    assert "Asignatura Inactiva" not in contenido


@pytest.mark.django_db
def test_listado_de_asignaturas_permite_filtrar_por_inactivas(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura Activa", programa=programa, activa=True)
    baker.make(Asignatura, nombre="Asignatura Inactiva", programa=programa, activa=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"), {"estado": "inactivas"})
    contenido = respuesta.content.decode()

    assert "Asignatura Inactiva" in contenido
    assert "Asignatura Activa" not in contenido


@pytest.mark.django_db
def test_listado_de_asignaturas_permite_filtrar_por_todas(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura Activa", programa=programa, activa=True)
    baker.make(Asignatura, nombre="Asignatura Inactiva", programa=programa, activa=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"), {"estado": "todas"})
    contenido = respuesta.content.decode()

    assert "Asignatura Activa" in contenido
    assert "Asignatura Inactiva" in contenido


@pytest.mark.django_db
def test_listado_de_asignaturas_muestra_el_programa_de_cada_asignatura(client):
    programa_1 = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    programa_2 = baker.make(Programa, nombre="Medicina", activo=True)
    baker.make(Asignatura, nombre="Programación I", programa=programa_1, codigo="SIS101", activa=True)
    baker.make(Asignatura, nombre="Anatomía", programa=programa_2, codigo="MED101", activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"))
    contenido = respuesta.content.decode()

    assert "Ingeniería de Sistemas" in contenido
    assert "Medicina" in contenido


@pytest.mark.django_db
def test_listado_de_asignaturas_permite_filtrar_por_programa(client):
    programa_1 = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    programa_2 = baker.make(Programa, nombre="Medicina", activo=True)
    baker.make(Asignatura, nombre="Programación I", programa=programa_1, codigo="SIS101", activa=True)
    baker.make(Asignatura, nombre="Programación II", programa=programa_2, codigo="MED101", activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(
        reverse("academico:asignatura_lista"), {"programa": programa_1.pk}
    )
    contenido = respuesta.content.decode()

    assert "Programación I" in contenido
    assert "Programación II" not in contenido


@pytest.mark.django_db
def test_listado_ofrece_reactivar_para_una_asignatura_inactiva(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura Inactiva", programa=programa, activa=False)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"), {"estado": "todas"})
    contenido = respuesta.content.decode()

    assert "Reactivar" in contenido
    assert "Desactivar" not in contenido


@pytest.mark.django_db
def test_listado_ofrece_desactivar_para_una_asignatura_activa(client):
    programa = baker.make(Programa, activo=True)
    baker.make(Asignatura, nombre="Asignatura Activa", programa=programa, activa=True)
    client.force_login(crear_administrador())

    respuesta = client.get(reverse("academico:asignatura_lista"))
    contenido = respuesta.content.decode()

    assert "Desactivar" in contenido
    assert "Reactivar" not in contenido


@pytest.mark.django_db
def test_administrador_puede_crear_una_asignatura(client):
    programa = baker.make(Programa, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa.pk,
            "codigo": "SIS101",
            "nombre": "Introducción a la Programación",
            "creditos": 3,
            "activa": True,
        },
    )

    assert respuesta.status_code == 302
    assert Asignatura.objects.filter(
        nombre="Introducción a la Programación", codigo="SIS101", programa=programa
    ).exists()


@pytest.mark.django_db
def test_no_crea_asignatura_sin_codigo(client):
    programa = baker.make(Programa, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa.pk,
            "codigo": "",
            "nombre": "Asignatura sin código",
            "creditos": 3,
            "activa": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    assert Asignatura.objects.count() == 0


@pytest.mark.django_db
def test_no_crea_asignatura_sin_nombre(client):
    programa = baker.make(Programa, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa.pk,
            "codigo": "SIS101",
            "nombre": "",
            "creditos": 3,
            "activa": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    assert Asignatura.objects.count() == 0


@pytest.mark.django_db
def test_no_crea_asignatura_sin_creditos(client):
    programa = baker.make(Programa, activo=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa.pk,
            "codigo": "SIS101",
            "nombre": "Asignatura sin créditos",
            "creditos": "",
            "activa": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    assert Asignatura.objects.count() == 0


@pytest.mark.django_db
def test_no_crea_asignatura_con_codigo_duplicado_en_mismo_programa(client):
    programa = baker.make(Programa, activo=True)
    # Crear primera asignatura
    baker.make(Asignatura, nombre="Asignatura Existente", programa=programa, codigo="SIS101", activa=True)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa.pk,
            "codigo": "SIS101",  # Código duplicado en el mismo programa
            "nombre": " Nueva Asignatura",
            "creditos": 4,
            "activa": True,
        },
    )

    assert respuesta.status_code == 200  # Vuelve a mostrar el formulario con errores
    # Verificar que solo existe una asignatura (la primera)
    assert Asignatura.objects.filter(codigo="SIS101", programa=programa).count() == 1


@pytest.mark.django_db
def test_si_puede_crear_asignatura_con_mismo_codigo_en_programa_diferente(client):
    programa_1 = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    programa_2 = baker.make(Programa, nombre="Medicina", activo=True)
    # Crear asignatura en el primer programa
    baker.make(Asignatura, nombre="Programación I", programa=programa_1, codigo="SIS101", activa=True)
    client.force_login(crear_administrador())

    # Debe poder crear asignatura con mismo código en segundo programa
    respuesta = client.post(
        reverse("academico:asignatura_crear"),
        data={
            "programa": programa_2.pk,
            "codigo": "SIS101",  # Mismo código pero en programa diferente
            "nombre": "Fundamentos de Programación",
            "creditos": 3,
            "activa": True,
        },
    )

    assert respuesta.status_code == 302  # Redirección exitosa
    # Verificar que existen ambas asignaturas
    assert Asignatura.objects.filter(codigo="SIS101").count() == 2
    assert Asignatura.objects.filter(programa=programa_1, codigo="SIS101").exists()
    assert Asignatura.objects.filter(programa=programa_2, codigo="SIS101").exists()


@pytest.mark.django_db
def test_administrador_puede_modificar_una_asignatura(client):
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(
        Asignatura, nombre="Nombre viejo", codigo="VIEJO101", creditos=2, programa=programa
    )
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_editar", args=[asignatura.pk]),
        data={
            "programa": programa.pk,
            "codigo": "NUEVO101",
            "nombre": "Nombre nuevo",
            "creditos": 4,
            "activa": False,
        },
    )
    asignatura.refresh_from_db()

    assert respuesta.status_code == 302
    assert asignatura.nombre == "Nombre nuevo"
    assert asignatura.codigo == "NUEVO101"
    assert asignatura.creditos == 4
    assert asignatura.activa is False


@pytest.mark.django_db
def test_desactivar_asignatura_no_la_elimina_fisicamente(client):
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(Asignatura, activa=True, programa=programa)
    client.force_login(crear_administrador())

    respuesta = client.post(
        reverse("academico:asignatura_desactivar", args=[asignatura.pk])
    )
    asignatura.refresh_from_db()

    assert respuesta.status_code == 302
    assert Asignatura.objects.filter(pk=asignatura.pk).exists()
    assert asignatura.activa is False


@pytest.mark.django_db
def test_reactivar_asignatura_la_vuelve_a_marcar_como_activa(client):
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(Asignatura, activa=False, programa=programa)
    client.force_login(crear_administrador())

    respuesta = client.post(reverse("academico:asignatura_reactivar", args=[asignatura.pk]))
    asignatura.refresh_from_db()

    assert respuesta.status_code == 302
    assert asignatura.activa is True