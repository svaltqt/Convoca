from django.db import transaction

from apps.propuestas.models import Adhesion, Propuesta

ESTADOS_CON_RETIRO = (Propuesta.Estado.ABIERTA, Propuesta.Estado.QUORUM)


def eliminar_cuenta(usuario):
    """
    Eliminación de cuenta (HU-17, regla 18): cada adhesión a una propuesta
    ABIERTA o QUORUM se elimina con la propuesta bloqueada y su estado se
    recalcula. Luego la cuenta se desactiva. Todo en una sola transacción.

    No usa Adhesion.delete() porque ese es el retiro voluntario y exige
    periodo abierto (regla 11); la eliminación de cuenta es un derecho de
    supresión (Ley 1581) y procede aunque el periodo esté cerrado.

    Las adhesiones a propuestas RADICADA o posteriores se conservan (regla
    19). El usuario siempre se anonimiza. La cuenta no se borra
    físicamente: creador y usuario de adhesión son PROTECT.
    """
    with transaction.atomic():
        adhesiones = list(
            Adhesion.objects.filter(
                usuario=usuario, propuesta__estado__in=ESTADOS_CON_RETIRO
            )
        )
        for adhesion in adhesiones:
            propuesta = Propuesta.objects.select_for_update().get(
                pk=adhesion.propuesta_id
            )
            if propuesta.estado not in ESTADOS_CON_RETIRO:
                continue
            Adhesion.objects.filter(pk=adhesion.pk).delete()
            propuesta.recalcular_estado_tras_retiro()

        anonimizar(usuario)
        usuario.is_active = False
        usuario.save(update_fields=["is_active", "first_name", "last_name", "email"])


def anonimizar(usuario):
    """
    Derecho de supresión (Ley 1581, RNF-02): al eliminar la cuenta no quedan
    datos personales reales, tenga o no adhesiones conservadas (regla 19).
    El correo se construye con el pk para que siga siendo único; el dominio
    .invalid está reservado (RFC 2606) y nunca recibe correo.
    """
    usuario.first_name = "Usuario"
    usuario.last_name = "eliminado"
    usuario.email = f"eliminado-{usuario.pk}@anonimo.invalid"
