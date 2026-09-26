from django.db import migrations

NOMBRE_GRUPO_ADMINISTRADOR = "Administrador"
NOMBRE_GRUPO_ESTUDIANTE = "Estudiante"


def crear_grupos_y_migrar_administradores(apps, schema_editor):
    """
    Crea los grupos de roles (tarea 1.3) y agrega al grupo Administrador a
    todo usuario que ya tenga is_staff=True, para que nadie pierda acceso a
    las vistas de maestras al desplegar este cambio.
    """
    Group = apps.get_model("auth", "Group")
    Usuario = apps.get_model("usuarios", "Usuario")

    grupo_administrador, _ = Group.objects.get_or_create(name=NOMBRE_GRUPO_ADMINISTRADOR)
    Group.objects.get_or_create(name=NOMBRE_GRUPO_ESTUDIANTE)

    for usuario in Usuario.objects.filter(is_staff=True):
        usuario.groups.add(grupo_administrador)


def eliminar_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(
        name__in=[NOMBRE_GRUPO_ADMINISTRADOR, NOMBRE_GRUPO_ESTUDIANTE]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_usuario_programa"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            crear_grupos_y_migrar_administradores, eliminar_grupos
        ),
    ]
