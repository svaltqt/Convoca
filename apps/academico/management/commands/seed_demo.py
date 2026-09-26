import datetime
import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.academico.models import Asignatura, Docente, Facultad, Programa
from apps.periodos.models import Periodo
from apps.propuestas.models import Adhesion, Propuesta
from apps.usuarios.models import Usuario

SEMILLA_ALEATORIA = 20260926

DOMINIO_CORREO = "elpoli.edu.co"

FACULTADES = [
    "Facultad de Ingenierías",
    "Facultad de Ciencias Económicas y Administrativas",
]

PROGRAMAS = [
    ("Ingeniería de Sistemas", "IS", FACULTADES[0]),
    ("Ingeniería Industrial", "II", FACULTADES[0]),
    ("Administración de Empresas", "AE", FACULTADES[1]),
    ("Contaduría Pública", "CP", FACULTADES[1]),
]

ASIGNATURAS_CICLO_BASICO = [
    "Cálculo I",
    "Cálculo II",
    "Cálculo III",
    "Álgebra Lineal",
    "Ecuaciones Diferenciales",
    "Física I: Mecánica",
    "Física II: Electricidad y Magnetismo",
    "Física III: Ondas y Óptica",
    "Química General",
    "Programación I",
    "Programación II",
    "Algoritmos y Estructuras de Datos",
    "Base de Datos I",
    "Sistemas Operativos",
    "Circuitos Eléctricos I",
    "Estadística y Probabilidad",
    "Dibujo Técnico",
    "Introducción a la Ingeniería",
    "Cátedra Institucional Poli",
    "Ética y Ciudadanía",
    "Inglés I",
    "Inglés II",
    "Metodología de la Investigación",
    "Termodinámica",
    "Mecánica de Materiales",
    "Procesos Industriales",
    "Gestión de la Calidad",
    "Costos y Presupuestos",
    "Microeconomía",
    "Macroeconomía",
    "Contabilidad General",
    "Matemática Financiera",
]

DOCENTES = [
    "Martha Lucía Restrepo",
    "Carlos Alberto Zapata",
    "Diana Patricia Uribe",
    "Jorge Iván Cardona",
    "Lina María Betancur",
    "Andrés Felipe Osorio",
    "Sandra Milena Correa",
    "Gustavo Adolfo Vélez",
]

NOMBRES_ESTUDIANTES = [
    "Juan",
    "Camila",
    "Andrés",
    "Valentina",
    "Santiago",
    "Mariana",
    "Sebastián",
    "Isabella",
    "Carlos",
    "Daniela",
    "Felipe",
    "Laura",
    "Diego",
    "Natalia",
    "Julián",
    "Paula",
    "Alejandro",
    "Sofía",
    "Miguel",
    "Valeria",
]

APELLIDOS_ESTUDIANTES = [
    "García",
    "Rodríguez",
    "Martínez",
    "López",
    "González",
    "Pérez",
    "Sánchez",
    "Ramírez",
    "Torres",
    "Flórez",
    "Gómez",
    "Díaz",
    "Vargas",
    "Castro",
    "Ruiz",
    "Álvarez",
    "Romero",
    "Suárez",
    "Rojas",
    "Moreno",
]

NUM_ESTUDIANTES = 40


class Command(BaseCommand):
    help = "Carga datos de demostración: maestras, un periodo vacacional y propuestas en distintos estados."

    def handle(self, *args, **options):
        aleatorio = random.Random(SEMILLA_ALEATORIA)

        with transaction.atomic():
            self._borrar_datos_existentes()

            facultades = self._crear_facultades()
            programas = self._crear_programas(facultades)
            asignaturas = self._crear_asignaturas(programas, aleatorio)
            self._crear_docentes()
            periodo = self._crear_periodo()
            estudiantes = self._crear_estudiantes(programas)
            self._crear_propuestas_demo(asignaturas, periodo, estudiantes, aleatorio)

        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados."))

    def _borrar_datos_existentes(self):
        Adhesion.objects.all().delete()
        Propuesta.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()
        # Los superusuarios se conservan; si tienen programa, Usuario.programa
        # (PROTECT) impediría borrar los programas.
        Usuario.objects.update(programa=None)
        Asignatura.objects.all().delete()
        Docente.objects.all().delete()
        Programa.objects.all().delete()
        Facultad.objects.all().delete()
        Periodo.objects.all().delete()

    def _crear_facultades(self):
        return {nombre: Facultad.objects.create(nombre=nombre) for nombre in FACULTADES}

    def _crear_programas(self, facultades):
        return {
            codigo: Programa.objects.create(
                facultad=facultades[nombre_facultad],
                nombre=nombre,
                codigo=codigo,
            )
            for nombre, codigo, nombre_facultad in PROGRAMAS
        }

    def _crear_asignaturas(self, programas, aleatorio):
        codigos_programa = list(programas.keys())
        contadores = dict.fromkeys(codigos_programa, 101)
        asignaturas = {}
        for indice, nombre in enumerate(ASIGNATURAS_CICLO_BASICO):
            codigo_programa = codigos_programa[indice % len(codigos_programa)]
            codigo = f"{codigo_programa}{contadores[codigo_programa]}"
            contadores[codigo_programa] += 1
            asignaturas[nombre] = Asignatura.objects.create(
                programa=programas[codigo_programa],
                codigo=codigo,
                nombre=nombre,
                creditos=aleatorio.choice([2, 3, 4]),
            )
        return asignaturas

    def _crear_docentes(self):
        for indice, nombre in enumerate(DOCENTES, start=1):
            Docente.objects.create(
                nombre=nombre,
                email=f"docente{indice:02d}@{DOMINIO_CORREO}",
            )

    def _crear_periodo(self):
        hoy = timezone.localdate()
        return Periodo.objects.create(
            nombre="Vacacional 2026-1",
            inicio=hoy + datetime.timedelta(days=20),
            fin=hoy + datetime.timedelta(days=50),
            fecha_cierre_propuestas=hoy + datetime.timedelta(days=15),
            cupo_minimo=20,
            abierto=True,
        )

    def _crear_estudiantes(self, programas):
        codigos_programa = list(programas.keys())
        estudiantes = []
        for indice in range(1, NUM_ESTUDIANTES + 1):
            first_name = NOMBRES_ESTUDIANTES[indice % len(NOMBRES_ESTUDIANTES)]
            last_name = APELLIDOS_ESTUDIANTES[indice % len(APELLIDOS_ESTUDIANTES)]
            programa = programas[codigos_programa[indice % len(codigos_programa)]]
            usuario = Usuario.objects.create_user(
                email=f"estudiante{indice:02d}@{DOMINIO_CORREO}",
                password="estudiante123",
                first_name=first_name,
                last_name=last_name,
                programa=programa,
                autorizo_datos=True,
                fecha_autorizacion=timezone.now(),
            )
            estudiantes.append(usuario)
        return estudiantes

    def _crear_propuestas_demo(self, asignaturas, periodo, estudiantes, aleatorio):
        ahora = timezone.now()
        escenarios = [
            {
                "asignatura": "Programación I",
                "estado": Propuesta.Estado.ABIERTA,
                "num_adhesiones": 3,
                "dias_atras": 1,
            },
            {
                "asignatura": "Cálculo II",
                "estado": Propuesta.Estado.ABIERTA,
                "num_adhesiones": 12,
                "dias_atras": 4,
            },
            {
                "asignatura": "Física I: Mecánica",
                "estado": Propuesta.Estado.ABIERTA,
                "num_adhesiones": 18,
                "dias_atras": 6,
            },
            {
                "asignatura": "Estadística y Probabilidad",
                "estado": Propuesta.Estado.QUORUM,
                "num_adhesiones": 22,
                "dias_atras": 8,
            },
            {
                "asignatura": "Base de Datos I",
                "estado": Propuesta.Estado.RADICADA,
                "num_adhesiones": 21,
                "dias_atras": 10,
            },
            {
                "asignatura": "Circuitos Eléctricos I",
                "estado": Propuesta.Estado.RECHAZADA,
                "num_adhesiones": 20,
                "dias_atras": 12,
            },
        ]

        for escenario in escenarios:
            adherentes = aleatorio.sample(estudiantes, escenario["num_adhesiones"])
            # Toda propuesta nace ABIERTA (regla 6) y su creador queda
            # adherido automáticamente (regla 7), por eso se omite adherentes[0].
            propuesta = Propuesta.objects.create(
                asignatura=asignaturas[escenario["asignatura"]],
                periodo=periodo,
                creador=adherentes[0],
            )
            for usuario in adherentes[1:]:
                Adhesion.objects.create(propuesta=propuesta, usuario=usuario)
            propuesta.refresh_from_db()
            self._llevar_a_estado(propuesta, escenario["estado"])
            Propuesta.objects.filter(pk=propuesta.pk).update(
                creada=ahora - datetime.timedelta(days=escenario["dias_atras"])
            )

    def _llevar_a_estado(self, propuesta, estado):
        """
        ABIERTA→QUORUM ya ocurrió sola al alcanzar el cupo; RADICADA y los
        estados finales se alcanzan con las transiciones del administrador
        (regla 16), no escribiendo el estado directamente.
        """
        if estado in (
            Propuesta.Estado.RADICADA,
            Propuesta.Estado.APROBADA,
            Propuesta.Estado.RECHAZADA,
        ):
            propuesta.cambiar_estado(Propuesta.Estado.RADICADA)
        if estado in (Propuesta.Estado.APROBADA, Propuesta.Estado.RECHAZADA):
            propuesta.cambiar_estado(estado)
