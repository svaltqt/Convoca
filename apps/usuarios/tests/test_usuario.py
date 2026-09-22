import pytest

from apps.usuarios.models import Usuario


@pytest.mark.django_db
def test_usuario_nuevo_no_tiene_autorizacion_de_datos():
    usuario = Usuario.objects.create_user(
        email="prueba@elpoli.edu.co",
        password="clave-de-prueba",
    )

    assert usuario.autorizo_datos is False


@pytest.mark.django_db
def test_usuario_se_identifica_por_correo():
    usuario = Usuario.objects.create_user(
        email="prueba2@elpoli.edu.co",
        password="clave-de-prueba",
    )

    assert usuario.get_username() == "prueba2@elpoli.edu.co"