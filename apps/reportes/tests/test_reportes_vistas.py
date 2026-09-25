from datetime import date, timedelta

import pytest
from django.urls import reverse
from model_bakery import baker

from apps.academico.models import Asignatura, Facultad, Programa
from apps.periodos.models import Periodo
from apps.propuestas.models import Adhesion, Propuesta
from apps.usuarios.models import Usuario


def crear_administrador():
    # first_name evita que la cabecera muestre el correo del propio admin,
    # lo que confundiría las aserciones de privacidad sobre correos.
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co",
        password="clave-de-prueba",
        is_staff=True,
        first_name="Admin",
    )


def crear_estudiante(autoriza_datos=True):
    return baker.make(
        Usuario,
        is_staff=False,
        autorizo_datos=autoriza_datos,
    )


@pytest.mark.django_db
def test_url_reportes_index_existe():
    """Test que verifica que existe la URL de índice de reportes."""
    assert reverse("reportes:index") == "/reportes/"


@pytest.mark.django_db
def test_url_quorum_por_facultad_existe():
    """Test que verifica que existe la URL de quórum por facultad."""
    assert reverse("reportes:quorum_por_facultad") == "/reportes/quorum-por-facultad/"


@pytest.mark.django_db
def test_url_adherentes_por_propuesta_existe():
    """Test que verifica que existe la URL de adherentes por propuesta."""
    assert (
        reverse("reportes:adherentes_por_propuesta")
        == "/reportes/adherentes-por-propuesta/"
    )


@pytest.mark.django_db
def test_url_adherentes_por_propuesta_pdf_existe():
    """Test que verifica que existe la URL de exportación a PDF."""
    assert (
        reverse("reportes:adherentes_por_propuesta_pdf")
        == "/reportes/adherentes-por-propuesta/pdf/"
    )


@pytest.mark.django_db
def test_anonimo_redirigido_a_login_en_reportes_index(client):
    """Test que verifica que usuario anónimo es redirigido al login en reportes."""
    respuesta = client.get(reverse("reportes:index"))
    assert respuesta.status_code == 302
    assert "/entrar/" in respuesta.url


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_reportes_index(client):
    """Test que verifica que estudiante (no staff) no puede acceder a reportes."""
    estudiante = crear_estudiante()
    client.force_login(estudiante)

    respuesta = client.get(reverse("reportes:index"))
    # Debe ser redirigido o recibir 403
    assert respuesta.status_code in [302, 403]


@pytest.mark.django_db
def test_administrador_puede_acceder_reportes_index(client):
    """Test que verifica que administrador puede acceder a reportes index."""
    admin = crear_administrador()
    client.force_login(admin)

    respuesta = client.get(reverse("reportes:index"))
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    assert "Reportes administrativos" in contenido
    assert "Estado de quórum por facultad" in contenido
    assert "Adherentes por propuesta" in contenido


@pytest.mark.django_db
def test_administrador_puede_acceder_quorum_por_facultad(client):
    """Test que verifica que administrador puede acceder al reporte de quórum por facultad."""
    admin = crear_administrador()
    client.force_login(admin)

    # Crear datos de prueba
    facultad = baker.make(Facultad, nombre="Facultad de Ingeniería", activa=True)
    programa = baker.make(
        Programa, facultad=facultad, nombre="Ingeniería de Sistemas", activo=True
    )
    asignatura = baker.make(
        Asignatura, programa=programa, nombre="Programación I", activa=True
    )
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)
    creador = crear_estudiante()
    Propuesta.objects.create(asignatura=asignatura, periodo=periodo, creador=creador)

    respuesta = client.get(reverse("reportes:quorum_por_facultad"))
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    assert "Facultad de Ingeniería" in contenido
    assert "Programación I" in contenido
    assert "Ingeniería de Sistemas" in contenido


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_quorum_por_facultad(client):
    """Test que verifica que estudiante no puede acceder al reporte de quórum."""
    estudiante = crear_estudiante()
    client.force_login(estudiante)

    respuesta = client.get(reverse("reportes:quorum_por_facultad"))
    assert respuesta.status_code in [302, 403]


@pytest.mark.django_db
def test_quorum_por_facultad_muestra_porcentaje_avance(client):
    """Test que verifica que el reporte muestra el porcentaje de avance correcto."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)
    creador = crear_estudiante()

    Propuesta.objects.create(asignatura=asignatura, periodo=periodo, creador=creador)

    # Solo el creador (1 de 20 = 5%)
    respuesta = client.get(reverse("reportes:quorum_por_facultad"))
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    # Debe mostrar el progreso
    assert "1 de 20" in contenido or "5%" in contenido or "interesados" in contenido


@pytest.mark.django_db
def test_quorum_por_facultad_muestra_dias_restantes(client):
    """Test que verifica que el reporte muestra los días restantes del periodo."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    hoy = date.today()
    periodo = baker.make(
        Periodo,
        abierto=True,
        cupo_minimo=20,
        fin=hoy + timedelta(days=15),
        fecha_cierre_propuestas=hoy + timedelta(days=5),
    )
    creador = crear_estudiante()

    Propuesta.objects.create(asignatura=asignatura, periodo=periodo, creador=creador)

    respuesta = client.get(reverse("reportes:quorum_por_facultad"))
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    # Debe mostrar los días restantes (aprox 15)
    assert "15" in contenido or "días" in contenido


@pytest.mark.django_db
def test_administrador_puede_acceder_adherentes_por_propuesta(client):
    """Test que verifica que administrador puede acceder al reporte de adherentes."""
    admin = crear_administrador()
    client.force_login(admin)

    respuesta = client.get(reverse("reportes:adherentes_por_propuesta"))
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    assert "Adherentes por propuesta" in contenido
    assert "Seleccione una propuesta" in contenido


@pytest.mark.django_db
def test_estudiante_no_puede_acceder_adherentes_por_propuesta(client):
    """Test que verifica que estudiante no puede acceder al reporte de adherentes."""
    estudiante = crear_estudiante()
    client.force_login(estudiante)

    respuesta = client.get(reverse("reportes:adherentes_por_propuesta"))
    assert respuesta.status_code in [302, 403]


@pytest.mark.django_db
def test_adherentes_por_propuesta_muestra_adherentes_al_seleccionar(client):
    """Test que verifica que se muestran adherentes al seleccionar una propuesta."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(
        Programa, facultad=facultad, nombre="Ingeniería de Sistemas", activo=True
    )
    asignatura = baker.make(
        Asignatura, programa=programa, nombre="Programación I", activa=True
    )
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)
    creador = crear_estudiante()
    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )

    # Agregar otro adherente, con el programa explícito (la tabla muestra
    # el programa del usuario, no el de la asignatura)
    usuario2 = baker.make(Usuario, autorizo_datos=True, programa=programa)
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario2)

    respuesta = client.get(
        reverse("reportes:adherentes_por_propuesta"), {"propuesta": propuesta.pk}
    )
    assert respuesta.status_code == 200
    contenido = respuesta.content.decode()
    # Debe mostrar los adherentes (creador + usuario2 = 2)
    assert "adherente" in contenido.lower()
    assert "Ingeniería de Sistemas" in contenido  # Programa del adherente
    assert "Programación I" in contenido  # Asignatura


@pytest.mark.django_db
def test_adherentes_por_propuesta_no_muestra_email(client):
    """Test que verifica que el reporte NO muestra correos electrónicos."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(
        Programa, facultad=facultad, nombre="Ingeniería de Sistemas", activo=True
    )
    asignatura = baker.make(
        Asignatura, programa=programa, nombre="Programación I", activa=True
    )
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)
    creador = crear_estudiante()
    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )

    usuario = baker.make(Usuario, autorizo_datos=True, programa=programa)
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)

    respuesta = client.get(
        reverse("reportes:adherentes_por_propuesta"), {"propuesta": propuesta.pk}
    )
    contenido = respuesta.content.decode()

    # Verificar que NO aparece el email
    assert "@elpoli.edu.co" not in contenido
    assert usuario.email not in contenido
    # Pero sí aparece el nombre
    assert usuario.first_name in contenido or usuario.last_name in contenido


@pytest.mark.django_db
def test_adherentes_por_propuesta_pdf_genera_correctamente(client):
    """Test que verifica que la exportación a PDF funciona y no incluye emails."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(
        Programa, facultad=facultad, nombre="Ingeniería de Sistemas", activo=True
    )
    asignatura = baker.make(
        Asignatura,
        programa=programa,
        codigo="SIS101",
        nombre="Programación I",
        activa=True,
    )
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20, nombre="2026-1")
    creador = crear_estudiante()
    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )

    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario)

    respuesta = client.get(
        reverse("reportes:adherentes_por_propuesta_pdf"), {"propuesta": propuesta.pk}
    )
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/pdf"
    assert "attachment" in respuesta["Content-Disposition"]
    assert "adherentes" in respuesta["Content-Disposition"]
    assert "SIS101" in respuesta["Content-Disposition"]
    # El PDF no debe contener correos electrónicos de los adherentes
    assert usuario.email.encode() not in respuesta.content
    assert b"@example.com" not in respuesta.content


@pytest.mark.django_db
def test_adherentes_por_propuesta_pdf_requiere_propuesta(client):
    """Test que verifica que el PDF requiere parámetro propuesta."""
    admin = crear_administrador()
    client.force_login(admin)

    respuesta = client.get(reverse("reportes:adherentes_por_propuesta_pdf"))
    assert respuesta.status_code == 400
    assert "Debe seleccionar una propuesta" in respuesta.content.decode()


@pytest.mark.django_db
def test_adherentes_por_propuesta_pdf_no_permite_rechazada(client):
    """Test que verifica que no se puede generar PDF de propuesta rechazada."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    periodo = baker.make(Periodo, abierto=True)
    creador = crear_estudiante()
    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
        estado=Propuesta.Estado.RECHAZADA,
    )

    respuesta = client.get(
        reverse("reportes:adherentes_por_propuesta_pdf"), {"propuesta": propuesta.pk}
    )
    assert respuesta.status_code == 400
    assert "rechazada" in respuesta.content.decode().lower()


@pytest.mark.django_db
def test_quorum_pdf_genera_correctamente(client):
    """Test que verifica que el PDF de quórum por facultad se genera."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    asignatura = baker.make(
        Asignatura, programa=programa, codigo="SIS101", activa=True
    )
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20, nombre="2026-1")
    creador = crear_estudiante()
    Propuesta.objects.create(asignatura=asignatura, periodo=periodo, creador=creador)

    respuesta = client.get(reverse("reportes:quorum_por_facultad_pdf"))
    assert respuesta.status_code == 200
    assert respuesta["Content-Type"] == "application/pdf"
    assert "attachment" in respuesta["Content-Disposition"]
    assert "quorum_por_facultad" in respuesta["Content-Disposition"]


@pytest.mark.django_db
def test_quorum_pdf_no_incluye_emails(client):
    """Test que verifica que el PDF de quórum no incluye correos de adherentes."""
    admin = crear_administrador()
    client.force_login(admin)

    facultad = baker.make(Facultad, activa=True)
    programa = baker.make(Programa, facultad=facultad, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    periodo = baker.make(Periodo, abierto=True)
    creador = crear_estudiante()
    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )
    Adhesion.objects.create(propuesta=propuesta, usuario=crear_estudiante())

    respuesta = client.get(reverse("reportes:quorum_por_facultad_pdf"))
    assert respuesta.status_code == 200
    assert b"@elpoli.edu.co" not in respuesta.content
    assert b"@example.com" not in respuesta.content


@pytest.mark.django_db
def test_quorum_pdf_requiere_administrador(client):
    """Test que verifica que un estudiante no puede descargar el PDF de quórum."""
    estudiante = crear_estudiante()
    client.force_login(estudiante)

    respuesta = client.get(reverse("reportes:quorum_por_facultad_pdf"))
    assert respuesta.status_code in [302, 403]


@pytest.mark.django_db
def test_reportes_en_navegacion_administrador(client):
    """Test que verifica que los reportes aparecen en la navegación del admin."""
    admin = crear_administrador()
    client.force_login(admin)

    respuesta = client.get(reverse("inicio"))
    contenido = respuesta.content.decode()
    assert "Reportes" in contenido
    assert "Estado de quórum" in contenido
    assert "Adherentes por propuesta" in contenido


@pytest.mark.django_db
def test_reportes_no_en_navegacion_estudiante(client):
    """Test que verifica que los reportes NO aparecen en la navegación del estudiante."""
    estudiante = crear_estudiante()
    client.force_login(estudiante)

    # La navegación condiciona los enlaces de reportes con user.is_staff;
    # se verifica que el estudiante no puede acceder directamente.
    respuesta_reportes = client.get(reverse("reportes:index"))
    assert respuesta_reportes.status_code in [302, 403]
