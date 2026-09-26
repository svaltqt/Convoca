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

    La cuenta no se borra físicamente: creador y usuario de adhesión son
    PROTECT, y el criterio 3 necesitará conservar la fila para anonimizarla.
    Las adhesiones a propuestas RADICADA o posteriores no se tocan aquí.
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
        usuario.is_active = False
        usuario.save(update_fields=["is_active"])
