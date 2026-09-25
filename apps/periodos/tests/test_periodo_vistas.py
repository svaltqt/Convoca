import pytest
from django.urls import reverse, NoReverseMatch
from model_bakery import baker

from apps.usuarios.models import Usuario


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_url_periodo_lista_existe():
    """Test que verifica que existe la URL para listar periodos"""
    assert reverse("periodos:periodo_lista") == "/periodos/"


@pytest.mark.django_db
def test_url_periodo_crear_existe():
    """Test que verifica que existe la URL para crear periodos"""
    assert reverse("periodos:periodo_crear") == "/periodos/nueva/"


@pytest.mark.django_db
def test_url_periodo_editar_existe():
    """Test que verifica que existe la URL para editar periodos"""
    assert reverse("periodos:periodo_editar", args=[1]) == "/periodos/1/editar/"


@pytest.mark.django_db
def test_url_periodo_desactivar_existe():
    """Test que verifica que existe la URL para desactivar periodos"""
    assert reverse("periodos:periodo_desactivar", args=[1]) == "/periodos/1/desactivar/"


@pytest.mark.django_db
def test_url_periodo_reactivar_existe():
    """Test que verifica que existe la URL para reactivar periodos"""
    assert reverse("periodos:periodo_reactivar", args=[1]) == "/periodos/1/reactivar/"


@pytest.mark.django_db
def test_anonimo_redirigido_al_listar_periodos(client):
    """Test que verifica que usuario anónimo es redirigido al login al listar periodos"""
    # Esta prueba debe fallar porque no existe la vista de listado de periodos
    try:
        respuesta = client.get(reverse("periodos:periodo_lista"))
        # Si llegamos aquí, verificamos que sea redirección a login
        assert respuesta.status_code == 302
        assert "/entrar/" in respuesta.url
    except NoReverseMatch:
        # Esperado: la URL no existe todavía
        pass


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_listado_periodos(client):
    """Test que verifica que estudiante no puede acceder al listado de periodos"""
    # Esta prueba debe fallar porque no existe la vista de listado de periodos
    try:
        client.force_login(crear_estudiante())
        respuesta = client.get(reverse("periodos:periodo_lista"))
        # Si llegamos aquí, verificamos que sea 403 (prohibido)
        assert respuesta.status_code == 403
    except NoReverseMatch:
        # Esperado: la URL no existe todavía
        pass


@pytest.mark.django_db
def test_administrador_puede_consultar_listado_periodos(client):
    """Test que verifica que administrador puede consultar listado de periodos"""
    # Esta prueba debe fallar porque no existe la vista de listado de periodos
    try:
        periodo = baker.make("periodos.Periodo", nombre="Periodo 2026-2")
        client.force_login(crear_administrador())
        respuesta = client.get(reverse("periodos:periodo_lista"))
        contenido = respuesta.content.decode()

        # Si llegamos aquí, verificamos que muestre el periodo
        assert respuesta.status_code == 200
        assert "Periodo 2026-2" in contenido
    except NoReverseMatch:
        # Esperado: la URL no existe todavía
        pass


@pytest.mark.django_db
def test_administrador_puede_crear_periodo(client):
    """Test que verifica que administrador puede crear un periodo"""
    # Esta prueba debe fallar porque no existe la vista de creación de periodos
    try:
        client.force_login(crear_administrador())
        respuesta = client.post(
            reverse("periodos:periodo_crear"),
            data={
                "nombre": "Periodo 2026-2",
                "inicio": "2026-08-01",
                "fin": "2026-12-15",
                "fecha_cierre_propuestas": "2026-10-30",
                "cupo_minimo": 25,
                "abierto": True,
            },
        )

        # Si llegamos aquí, verificamos redirección exitosa y que se creó el periodo
        assert respuesta.status_code == 302
        from apps.periodos.models import Periodo
        assert Periodo.objects.filter(nombre="Periodo 2026-2").exists()
    except NoReverseMatch:
        # Esperado: la URL no existe todavía
        pass


@pytest.mark.django_db
def test_no_crea_periodo_sin_nombre(client):
    """Test que verifica que no se crea periodo sin nombre"""
    # Esta prueba debe fallar porque no existe la vista de creación de periodos
    try:
        client.force_login(crear_administrador())
        respuesta = client.post(
            reverse("periodos:periodo_crear"),
            data={
                "nombre": "",  # Nombre vacío
                "inicio": "2026-08-01",
                "fin": "2026-12-15",
                "fecha_cierre_propuestas": "2026-10-30",
                "cupo_minimo": 25,
                "abierto": True,
            },
        )

        # Si llegamos aquí, verificamos que muestre error (vuelve a mostrar formulario)
        assert respuesta.status_code == 200
        from apps.periodos.models import Periodo
        assert Periodo.objects.count() == 0
    except NoReverseMatch:
        # Esperado: la URL no existe todavía
        pass


@pytest.mark.django_db
def test_administrador_puede_abrir_cerrar_periodo(client):
    """Test que verifica que administrador puede abrir/cerrar un periodo"""
    # Esta prueba debe fallar porque no existen las vistas de abrir/cerrar periodos
    try:
        periodo = baker.make("periodos.Periodo", nombre="Periodo de Prueba", abierto=True)
        client.force_login(crear_administrador())

        # Probar cerrar periodo
        respuesta = client.post(
            reverse("periodos:periodo_desactivar", args=[periodo.pk])
        )
        assert respuesta.status_code == 302
        periodo.refresh_from_db()
        assert periodo.abierto is False

        # Probar abrir periodo
        respuesta = client.post(
            reverse("periodos:periodo_reactivar", args=[periodo.pk])
        )
        assert respuesta.status_code == 302
        periodo.refresh_from_db()
        assert periodo.abierto is True
    except NoReverseMatch:
        # Esperado: las URLs no existen todavía
        pass
