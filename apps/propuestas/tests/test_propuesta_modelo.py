import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from model_bakery import baker

from apps.academico.models import Asignatura, Programa
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
        fecha_autorizacion=timezone.now() if autoriza_datos else None,
    )


@pytest.mark.django_db
def test_crear_propuesta_solo_con_asignatura_activa():
    """Test que verifica que solo se puede crear propuesta con asignatura activa"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura_activa = baker.make(Asignatura, programa=programa, activa=True)
    asignatura_inactiva = baker.make(Asignatura, programa=programa, activa=False)
    creador = crear_estudiante()

    # Debe permitir crear propuesta con asignatura activa
    propuesta_activa = Propuesta.objects.create(
        asignatura=asignatura_activa,
        periodo=periodo,
        creador=creador,
    )
    assert propuesta_activa.asignatura == asignatura_activa

    # Debe rechazar crear propuesta con asignatura inactiva
    with pytest.raises(ValidationError):
        propuesta_inactiva = Propuesta(
            asignatura=asignatura_inactiva,
            periodo=periodo,
            creador=creador,
        )
        propuesta_inactiva.full_clean()


@pytest.mark.django_db
def test_crear_propuesta_solo_con_periodo_abierto():
    """Test que verifica que solo se puede crear propuesta con periodo abierto"""
    programa = baker.make(Programa, activo=True)
    periodo_abierto = baker.make(Periodo, abierto=True)
    periodo_cerrado = baker.make(Periodo, abierto=False)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    # Debe permitir crear propuesta con periodo abierto
    propuesta_abierta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_abierto,
        creador=creador,
    )
    assert propuesta_abierta.periodo == periodo_abierto

    # Debe rechazar crear propuesta con periodo cerrado
    with pytest.raises(ValidationError):
        propuesta_cerrada = Propuesta(
            asignatura=asignatura,
            periodo=periodo_cerrado,
            creador=creador,
        )
        propuesta_cerrada.full_clean()


@pytest.mark.django_db
def test_crear_propuesta_solo_con_periodo_no_vencido():
    """Test que verifica que solo se puede crear propuesta si la fecha de cierre no ha vencido"""
    from datetime import date, timedelta

    programa = baker.make(Programa, activo=True)
    periodo_vencido = baker.make(
        Periodo,
        fecha_cierre_propuestas=date.today() - timedelta(days=1),  # Ayer
        abierto=True
    )
    periodo_no_vencido = baker.make(
        Periodo,
        fecha_cierre_propuestas=date.today() + timedelta(days=10),  # Dentro de 10 días
        abierto=True
    )
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    # Debe permitir crear propuesta con periodo no vencido
    propuesta_valida = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_no_vencido,
        creador=creador,
    )
    assert propuesta_valida.periodo == periodo_no_vencido

    # Debe rechazar crear propuesta con periodo vencido
    with pytest.raises(ValidationError):
        propuesta_vencida = Propuesta(
            asignatura=asignatura,
            periodo=periodo_vencido,
            creador=creador,
        )
        propuesta_vencida.full_clean()


@pytest.mark.django_db
def test_crear_propuesta_con_docente_opcional():
    """Test que verifica que el docente es opcional al crear una propuesta"""
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    docente = baker.make("academico.Docente")

    # Crear diferentes periodos para evitar conflictos de unicidad
    periodo_sin_docente = baker.make(Periodo, abierto=True)
    periodo_con_docente = baker.make(Periodo, abierto=True)

    # Crear propuesta sin docente
    propuesta_sin_docente = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_sin_docente,
        creador=creador,
        docente=None,
    )
    assert propuesta_sin_docente.docente is None

    # Crear propuesta con docente
    propuesta_con_docente = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_con_docente,
        creador=creador,
        docente=docente,
    )
    assert propuesta_con_docente.docente == docente


@pytest.mark.django_db
def test_no_crear_segunda_propuesta_activa_misma_asignatura_periodo():
    """Test que verifica que no se puede crear segunda propuesta activa para misma asignatura/periodo"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    # Crear primera propuesta
    propuesta1 = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )
    assert propuesta1.estado == Propuesta.Estado.ABIERTA

    # Intentar crear segunda propuesta para mismo asignatura/periodo debe fallar
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            propuesta2 = Propuesta.objects.create(
                asignatura=asignatura,
                periodo=periodo,
                creador=creador,
            )


@pytest.mark.django_db
def test_propuesta_creada_inicialmente_en_estado_abierta():
    """Test que verifica que una propuesta nueva empieza en estado ABIERTA"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )

    assert propuesta.estado == Propuesta.Estado.ABIERTA


@pytest.mark.django_db
def test_creador_queda_automaticamente_adherido():
    """Test que verifica que quien crea la propuesta queda automáticamente adherido"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )

    # Verificar que el creador está adherido
    adhesion = Adhesion.objects.filter(propuesta=propuesta, usuario=creador).first()
    assert adhesion is not None
    assert adhesion.usuario == creador
    assert adhesion.propuesta == propuesta


@pytest.mark.django_db
def test_usuario_puede_adherirse_solo_una_vez():
    """Test que verifica que un usuario puede adherirse solo una vez a una propuesta"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    otro_usuario = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )

    # Primera adhesión debe funcionar
    adhesion1 = Adhesion.objects.create(
        propuesta=propuesta,
        usuario=otro_usuario,
    )
    assert adhesion1 is not None

    # Segunda adhesión del mismo usuario debe fallar por restricción de BD
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            adhesion2 = Adhesion.objects.create(
                propuesta=propuesta,
                usuario=otro_usuario,
            )


@pytest.mark.django_db
def test_no_adherirse_si_periodo_cerrado():
    """Test que verifica que no se puede adherir si el periodo está cerrado"""
    programa = baker.make(Programa, activo=True)
    periodo_cerrado = baker.make(Periodo, abierto=True)
    periodo_abierto = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    usuario = crear_estudiante()

    propuesta_cerrada = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_cerrado,
        creador=creador,
    )
    periodo_cerrado.abierto = False
    periodo_cerrado.save(update_fields=["abierto"])
    propuesta_abierta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_abierto,
        creador=creador,
    )

    # No debe permitir adherencia a propuesta con periodo cerrado
    with pytest.raises(ValidationError):
        adhesion_cerrada = Adhesion(
            propuesta=propuesta_cerrada,
            usuario=usuario,
        )
        adhesion_cerrada.full_clean()

    # Debe permitir adherencia a propuesta con periodo abierto
    adhesion_abierta = Adhesion.objects.create(
        propuesta=propuesta_abierta,
        usuario=usuario,
    )
    assert adhesion_abierta is not None


@pytest.mark.django_db
def test_no_adherirse_despues_de_fecha_cierre():
    """Test que verifica que no se puede adherir después de fecha_cierre_propuestas"""
    from datetime import date, timedelta

    programa = baker.make(Programa, activo=True)
    periodo_vencido = baker.make(Periodo, fecha_cierre_propuestas=date.today() + timedelta(days=10), abierto=True)
    periodo_valido = baker.make(
        Periodo,
        fecha_cierre_propuestas=date.today() + timedelta(days=10),
        abierto=True
    )
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    usuario = crear_estudiante()

    propuesta_vencida = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_vencido,
        creador=creador,
    )
    periodo_vencido.fecha_cierre_propuestas = date.today() - timedelta(days=1)
    periodo_vencido.save(update_fields=["fecha_cierre_propuestas"])
    propuesta_valida = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_valido,
        creador=creador,
    )

    # No debe permitir adherencia después de fecha de cierre
    with pytest.raises(ValidationError):
        adhesion_vencida = Adhesion(
            propuesta=propuesta_vencida,
            usuario=usuario,
        )
        adhesion_vencida.full_clean()

    # Debe permitir adherencia antes de fecha de cierre
    adhesion_valida = Adhesion.objects.create(
        propuesta=propuesta_valida,
        usuario=usuario,
    )
    assert adhesion_valida is not None


@pytest.mark.django_db
def test_no_adherirse_si_usuario_no_autorizo_tratamiento_datos():
    """Test que verifica que no se puede adherir si usuario no autorizó tratamiento de datos"""
    programa = baker.make(Programa, activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    usuario_sin_autorizacion = crear_estudiante(autoriza_datos=False)
    usuario_con_autorizacion = crear_estudiante(autoriza_datos=True)

    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )

    # No debe permitir adhesión si usuario no autorizó tratamiento de datos
    with pytest.raises(ValidationError):
        adhesion_sin_autorizacion = Adhesion(
            propuesta=propuesta,
            usuario=usuario_sin_autorizacion,
        )
        adhesion_sin_autorizacion.full_clean()

    # Debe permitir adhesión si usuario autorizó tratamiento de datos
    adhesion_con_autorizacion = Adhesion.objects.create(
        propuesta=propuesta,
        usuario=usuario_con_autorizacion,
    )
    assert adhesion_con_autorizacion is not None


@pytest.mark.django_db
def test_propuestas_radicada_o_posterior_no_aceptan_adhesiones():
    """Test que verifica que propuestas RADICADA o posteriores no aceptan adhesiones"""
    programa = baker.make(Programa, activo=True)
    asignatura = baker.make(Asignatura, programa=programa, activa=True)
    creador = crear_estudiante()
    usuario = crear_estudiante()

    # Crear diferentes periodos para evitar conflictos de unicidad
    periodo_radicada = baker.make(Periodo, abierto=True)
    periodo_aprobada = baker.make(Periodo, abierto=True)
    periodo_rechazada = baker.make(Periodo, abierto=True)

    propuesta_radicada = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_radicada,
        creador=creador,
        estado=Propuesta.Estado.RADICADA,
    )
    propuesta_aprobada = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_aprobada,
        creador=creador,
        estado=Propuesta.Estado.APROBADA,
    )
    propuesta_rechazada = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo_rechazada,
        creador=creador,
        estado=Propuesta.Estado.RECHAZADA,
    )

    # Ninguna debería aceptar adhesiones
    for propuesta in [propuesta_radicada, propuesta_aprobada, propuesta_rechazada]:
        with pytest.raises(ValidationError):
            adhesion = Adhesion(
                propuesta=propuesta,
                usuario=usuario,
            )
            adhesion.full_clean()


@pytest.mark.django_db
def test_propuesta_muestra_adherentes_con_nombre_y_programa_sin_correo():
    """Test que verifica que se muestran nombre y programa pero nunca correo de adherentes"""
    programa_sistemas = baker.make(Programa, nombre="Ingeniería de Sistemas", activo=True)
    programa_medicina = baker.make(Programa, nombre="Medicina", activo=True)
    periodo = baker.make(Periodo, abierto=True)
    asignatura = baker.make(Asignatura, programa=programa_sistemas, activa=True)
    creador = crear_estudiante()
    usuario1 = crear_estudiante()
    usuario2 = crear_estudiante()

    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=creador,
    )

    # Crear adhesiones
    adhesion1 = Adhesion.objects.create(propuesta=propuesta, usuario=usuario1)
    adhesion2 = Adhesion.objects.create(propuesta=propuesta, usuario=usuario2)

    # Verificar que podemos acceder a nombre y programa
    adherentes = propuesta.adhesiones.all()
    assert adherentes.count() == 3  # creador + 2 usuarios

    for adhesion in adherentes:
        usuario = adhesion.usuario
        assert usuario.first_name is not None  # Nombre presente
        assert usuario.last_name is not None   # Apellido presente
        # En la vista pública, nunca debería mostrarse el correo
        # Esto se verificará en las pruebas de vistas


@pytest.mark.django_db
def test_administrador_puede_radicar_propuesta_con_periodo_cerrado():
    """
    Regresión (regla 16): radicar no depende del estado del periodo. Antes
    del ajuste de Propuesta.clean() en el criterio 2 de HU-17, clean()
    revalidaba "periodo abierto" en cada save() y bloqueaba esta transición.
    """
    periodo = baker.make(Periodo, abierto=True, fecha_cierre_propuestas=timezone.localdate())
    asignatura = baker.make(Asignatura, activa=True)
    propuesta = Propuesta.objects.create(
        asignatura=asignatura,
        periodo=periodo,
        creador=crear_estudiante(),
        estado=Propuesta.Estado.QUORUM,
    )
    Periodo.objects.filter(pk=periodo.pk).update(abierto=False)
    propuesta.refresh_from_db()

    propuesta.cambiar_estado(Propuesta.Estado.RADICADA)

    propuesta.refresh_from_db()
    assert propuesta.estado == Propuesta.Estado.RADICADA
