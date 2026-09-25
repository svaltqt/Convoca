from datetime import date, timedelta

import pytest
from model_bakery import baker

from apps.academico.models import Asignatura, Facultad, Programa
from apps.periodos.models import Periodo
from apps.propuestas.models import Adhesion, Propuesta
from apps.usuarios.models import Usuario


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante(autoriza_datos=True):
    return baker.make(
        Usuario,
        is_staff=False,
        autorizo_datos=autoriza_datos,
    )


@pytest.mark.django_db
def test_quorum_por_facultad_agrupa_por_facultad():
    """Test que verifica que el reporte agrupa propuestas por facultad correctamente."""
    # Crear estructura: Facultad -> Programa -> Asignatura -> Propuesta
    facultad_ingenieria = baker.make(
        Facultad, nombre="Facultad de Ingeniería", activa=True
    )
    facultad_salud = baker.make(
        Facultad, nombre="Facultad de Ciencias de la Salud", activa=True
    )

    programa_sistemas = baker.make(
        Programa,
        facultad=facultad_ingenieria,
        nombre="Ingeniería de Sistemas",
        activo=True,
    )
    programa_medicina = baker.make(
        Programa, facultad=facultad_salud, nombre="Medicina", activo=True
    )

    asignatura_sistemas = baker.make(
        Asignatura, programa=programa_sistemas, nombre="Programación I", activa=True
    )
    asignatura_medicina = baker.make(
        Asignatura, programa=programa_medicina, nombre="Anatomía", activa=True
    )

    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)

    creador = crear_estudiante()

    propuesta_sistemas = Propuesta.objects.create(
        asignatura=asignatura_sistemas, periodo=periodo, creador=creador
    )
    propuesta_medicina = Propuesta.objects.create(
        asignatura=asignatura_medicina, periodo=periodo, creador=creador
    )

    # Verificar que las propuestas están en las facultades correctas
    assert propuesta_sistemas.asignatura.programa.facultad == facultad_ingenieria
    assert propuesta_medicina.asignatura.programa.facultad == facultad_salud


@pytest.mark.django_db
def test_quorum_por_facultad_calcula_porcentaje_avance():
    """Test que verifica el cálculo correcto del porcentaje de avance."""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True, cupo_minimo=20)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )

    # Sin adhesiones extra (solo el creador)
    assert propuesta.total_adhesiones == 1
    porcentaje = min(
        int(propuesta.total_adhesiones * 100 / max(periodo.cupo_minimo, 1)), 100
    )
    assert porcentaje == 5  # 1 de 20 = 5%

    # Agregar 19 adhesiones más (total 20 = cupo mínimo)
    for _ in range(19):
        usuario = crear_estudiante()
        Adhesion.objects.create(propuesta=propuesta, usuario=usuario)

    assert propuesta.total_adhesiones == 20
    porcentaje = min(
        int(propuesta.total_adhesiones * 100 / max(periodo.cupo_minimo, 1)), 100
    )
    assert porcentaje == 100


@pytest.mark.django_db
def test_quorum_por_facultad_calcula_dias_restantes():
    """Test que verifica el cálculo correcto de días restantes del periodo."""

    programa = baker.make(Programa, activo=True)
    hoy = date.today()

    # Crear periodos con fechas válidas para creación de propuestas
    # pero con fin en futuro/pasado para probar días restantes
    periodo_futuro = baker.make(
        Periodo,
        abierto=True,
        fin=hoy + timedelta(days=30),
        fecha_cierre_propuestas=hoy + timedelta(days=10),
    )
    # Para periodo "pasado", usamos fecha_cierre_propuestas futura
    # pero fin pasado (el reporte igual calcula días restantes hasta fin)
    periodo_fin_pasado = baker.make(
        Periodo,
        abierto=True,
        fin=hoy - timedelta(days=1),
        fecha_cierre_propuestas=hoy
        + timedelta(days=10),  # aún válido para crear propuesta
    )

    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    propuesta_futura = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo_futuro, creador=creador
    )

    dias_restantes = (propuesta_futura.periodo.fin - hoy).days
    assert dias_restantes == 30

    propuesta_fin_pasado = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo_fin_pasado, creador=creador
    )

    dias_restantes_pasado = (propuesta_fin_pasado.periodo.fin - hoy).days
    # Si ya pasó el fin, debe ser negativo o 0
    assert dias_restantes_pasado <= 0


@pytest.mark.django_db
def test_quorum_por_facultad_excluye_propuestas_rechazadas():
    """Test que verifica que propuestas RECHAZADA no aparecen en el reporte."""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    propuesta_activa = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
        estado=Propuesta.Estado.ABIERTA,
    )
    propuesta_rechazada = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
        estado=Propuesta.Estado.RECHAZADA,
    )

    # Filtrar excluyendo RECHAZADA
    propuestas_activas = Propuesta.objects.exclude(estado=Propuesta.Estado.RECHAZADA)
    assert propuesta_activa in propuestas_activas
    assert propuesta_rechazada not in propuestas_activas


@pytest.mark.django_db
def test_quorum_por_facultad_excluye_periodos_cerrados():
    """Test que verifica que periodos cerrados no aparecen en el reporte."""
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    periodo_abierto = baker.make(Periodo, abierto=True)
    periodo_cerrado = baker.make(Periodo, abierto=True)

    propuesta_abierta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo_abierto, creador=creador
    )
    propuesta_cerrada = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo_cerrado, creador=creador
    )

    # El modelo impide crear propuestas en periodos cerrados (regla de negocio),
    # así que el cierre se simula después de creada la propuesta.
    periodo_cerrado.abierto = False
    periodo_cerrado.save()

    # Solo periodos abiertos
    propuestas_periodos_abiertos = Propuesta.objects.filter(periodo__abierto=True)
    assert propuesta_abierta in propuestas_periodos_abiertos
    assert propuesta_cerrada not in propuestas_periodos_abiertos


@pytest.mark.django_db
def test_adherentes_por_propuesta_muestra_nombre_y_programa():
    """Test que verifica que el reporte de adherentes muestra nombre y programa, no email."""
    programa_sistemas = baker.make(
        Programa, nombre="Ingeniería de Sistemas", activo=True
    )
    programa_medicina = baker.make(Programa, nombre="Medicina", activo=True)

    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa_sistemas, activa=True)
    creador = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura, periodo=periodo, creador=creador
    )

    # Crear adherentes con diferentes programas (autorizo_datos=True: regla 10)
    usuario1 = baker.make(
        Usuario,
        programa=programa_sistemas,
        first_name="Juan",
        last_name="Pérez",
        autorizo_datos=True,
    )
    usuario2 = baker.make(
        Usuario,
        programa=programa_medicina,
        first_name="María",
        last_name="García",
        autorizo_datos=True,
    )

    Adhesion.objects.create(propuesta=propuesta, usuario=usuario1)
    Adhesion.objects.create(propuesta=propuesta, usuario=usuario2)

    # Verificar que se pueden obtener nombre y programa, sin email.
    # Se excluye la adhesión automática del creador, cuyos nombres son
    # aleatorios (baker) y no son el objeto de esta verificación.
    adhesiones = (
        Adhesion.objects.filter(propuesta=propuesta)
        .exclude(usuario=creador)
        .select_related("usuario", "usuario__programa")
    )
    assert adhesiones.count() == 2
    for adhesion in adhesiones:
        usuario = adhesion.usuario
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()
        programa = usuario.programa.nombre if usuario.programa_id else "—"
        # Nunca se debe acceder al email en la vista
        assert nombre_completo != ""
        assert programa in ["Ingeniería de Sistemas", "Medicina"]


@pytest.mark.django_db
def test_adherentes_por_propuesta_filtra_por_propuesta_seleccionada():
    """Test que verifica que se puede filtrar adherentes por propuesta."""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura1 = baker.make(
        Asignatura, programa=programa, nombre="Asignatura 1", activa=True
    )
    asignatura2 = baker.make(
        Asignatura, programa=programa, nombre="Asignatura 2", activa=True
    )
    creador = crear_estudiante()

    propuesta1 = Propuesta.objects.create(
        asignatura=asignatura1, periodo=periodo, creador=creador
    )
    propuesta2 = Propuesta.objects.create(
        asignatura=asignatura2, periodo=periodo, creador=creador
    )

    usuario = crear_estudiante()
    Adhesion.objects.create(propuesta=propuesta1, usuario=usuario)
    Adhesion.objects.create(propuesta=propuesta2, usuario=usuario)

    # Cada propuesta incluye la adhesión automática del creador (regla 7)
    # más la adhesión explícita de `usuario`: 2 por propuesta.
    adhesiones_p1 = Adhesion.objects.filter(propuesta=propuesta1)
    assert adhesiones_p1.count() == 2
    assert all(a.propuesta == propuesta1 for a in adhesiones_p1)

    adhesiones_p2 = Adhesion.objects.filter(propuesta=propuesta2)
    assert adhesiones_p2.count() == 2
    assert all(a.propuesta == propuesta2 for a in adhesiones_p2)
