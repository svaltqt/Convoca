import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from apps.usuarios.models import Usuario
from apps.periodos.models import Periodo


def crear_administrador():
    return Usuario.objects.create_user(
        email="admin@elpoli.edu.co", password="clave-de-prueba", is_staff=True
    )


def crear_estudiante():
    return baker.make(Usuario, is_staff=False)


@pytest.mark.django_db
def test_periodo_creado_con_valores_predeterminados():
    """Test que verifica que un periodo se crea con cupo_minimo=20 y abierto=True por defecto"""
    periodo = baker.make(Periodo)

    assert periodo.cupo_minimo == 20
    assert periodo.abierto is True


@pytest.mark.django_db
def test_periodo_permite_establecer_nombre():
    """Test que verifica que se puede establecer el nombre del periodo"""
    periodo = baker.make(Periodo, nombre="Periodo Académico 2026-2")

    assert periodo.nombre == "Periodo Académico 2026-2"


@pytest.mark.django_db
def test_periodo_permite_establecer_fechas():
    """Test que verifica que se pueden establecer las fechas de inicio, fin y cierre de propuestas"""
    from datetime import date

    inicio = date(2026, 8, 1)
    fin = date(2026, 12, 15)
    fecha_cierre = date(2026, 10, 30)

    periodo = baker.make(
        Periodo,
        inicio=inicio,
        fin=fin,
        fecha_cierre_propuestas=fecha_cierre
    )

    assert periodo.inicio == inicio
    assert periodo.fin == fin
    assert periodo.fecha_cierre_propuestas == fecha_cierre


@pytest.mark.django_db
def test_periodo_permite_establecer_cupo_minimo():
    """Test que verifica que se puede establecer un cupo mínimo personalizado"""
    periodo = baker.make(Periodo, cupo_minimo=15)

    assert periodo.cupo_minimo == 15


@pytest.mark.django_db
def test_periodo_permite_abrir_y_cerrar():
    """Test que verifica que se puede abrir y cerrar un periodo"""
    periodo = baker.make(Periodo, abierto=True)

    # Verificar estado inicial
    assert periodo.abierto is True

    # Cerrar el periodo
    periodo.abierto = False
    periodo.save()
    periodo.refresh_from_db()

    assert periodo.abierto is False

    # Abrir el periodo nuevamente
    periodo.abierto = True
    periodo.save()
    periodo.refresh_from_db()

    assert periodo.abierto is True