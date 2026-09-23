# CLAUDE.md — Convoca

## Contexto del proyecto

**Convoca** es una aplicación web que permite a estudiantes del Politécnico Colombiano
Jaime Isaza Cadavid **proponer cursos vacacionales y reunir el quórum mínimo de
estudiantes** antes de la inscripción oficial.

Hoy ese proceso ocurre por voz a voz y grupos de WhatsApp. No existe plataforma para ver
qué cursos están reuniendo gente.

**Límite de alcance (crítico):** esta aplicación NO matricula ni inscribe. Registra
intención de matrícula. La inscripción oficial sigue siendo por Universitas XXI en la
fecha del calendario académico. Toda la UI debe reflejar esto: usar "interesados",
"apoyar propuesta", "me interesa". NUNCA "inscritos" ni "inscribirme".

Entrega académica. Fecha límite: 26 de septiembre de 2026.

Las historias de usuario con criterios de aceptación están en `docs/`. Cada test de la
lógica de negocio debe corresponder a un criterio de aceptación de esas historias.

## Stack

- Python 3.12+, **Django 6.1**
- PostgreSQL en Neon (psycopg + dj-database-url). Sin SQLite, ni siquiera en pruebas
- Plantillas de Django + HTMX + CSS propio. **Sin React, sin Node, sin build step**
- pytest + pytest-django + pytest-cov + pytest-html + model-bakery
- WeasyPrint para reportes PDF
- Gunicorn + WhiteNoise, desplegado en Render (región Ohio)
- Gestión de dependencias con `uv`. Todos los comandos se ejecutan con `uv run`

## Entornos y base de datos

La base de datos vive en Neon, región AWS US East 2 (Ohio). Cada integrante tiene su
propia rama de Neon:

| Rama de Neon | Uso |
|---|---|
| `production` | Solo Render. Nunca en el `.env` de nadie |
| `dev-infra` | Infraestructura y maestras |
| `dev-transaccional` | Propuestas y adhesiones |
| `dev-reportes` | Reportes y frontend |
| `dev-qa` | Pruebas y documentación |

- La conexión se define con `DATABASE_URL` en `.env`, usando la cadena **pooled**.
- Las ramas de Neon nunca se fusionan. La estructura llega a producción mediante las
  migraciones de Django, que se ejecutan en el despliegue.
- Si una rama de desarrollo se desincroniza, se borra y se recrea desde `production`.
- Settings divididos: `config/settings/base.py`, `local.py` (desarrollo en el PC) y
  `production.py` (Render).

## Modelo de datos

    Facultad 1─n Programa 1─n Asignatura
    Asignatura 1─n Propuesta n─1 Periodo
    Docente 1─n Propuesta (sugerido, opcional)
    Usuario 1─n Propuesta (creador)
    Propuesta 1─n Adhesion n─1 Usuario
    Programa 1─n Usuario

Apps (dentro de `apps/`): `usuarios`, `academico` (facultad, programa, asignatura,
docente), `periodos`, `propuestas` (propuesta, adhesion), `reportes`.

Campos clave:

- `Usuario`: modelo personalizado (`AUTH_USER_MODEL = "usuarios.Usuario"`).
  **Inicia sesión con correo**: sin campo `username`, `USERNAME_FIELD = "email"`,
  manager propio `UsuarioManager`. Campos: email institucional (único), first_name,
  last_name, programa (FK nullable, se agrega al crear `academico`), autorizo_datos,
  fecha_autorizacion. **No se almacena código estudiantil ni cédula.**
- `Facultad`: nombre, activa
- `Programa`: facultad, nombre, codigo, activo
- `Asignatura`: programa, codigo, nombre, creditos, activa
- `Docente`: nombre, email, disponible, activo
- `Periodo`: nombre, inicio, fin, fecha_cierre_propuestas, cupo_minimo (default 20),
  abierto
- `Propuesta`: asignatura, periodo, creador, docente (opcional), estado, creada
- `Adhesion`: propuesta, usuario, creada

## Reglas de negocio

Estas son la fuente de verdad. Si el código contradice esta sección, el código está mal.

### Registro y acceso

1. El registro solo acepta correos del dominio institucional. Otros dominios se rechazan
   con mensaje de error.
2. La autorización de tratamiento de datos aparece sin marcar por defecto, es
   obligatoria para completar el registro, y se guarda con fecha y hora.
3. El login es con correo institucional y contraseña.

### Propuestas

4. Solo se puede proponer sobre asignaturas activas y periodos abiertos cuya
   `fecha_cierre_propuestas` no haya vencido.
5. No puede existir más de una propuesta activa para la misma `(asignatura, periodo)`. Se considera activa toda propuesta en cualquier estado distinto de RECHAZADA.
6. Toda propuesta nueva empieza en estado `ABIERTA`.
7. **Quien crea la propuesta queda automáticamente adherido a ella.**

### Adhesiones

8. Un usuario puede adherirse **una sola vez** a una propuesta. Restricción única en BD
   `(propuesta, usuario)`, no solo validación en el formulario.
9. No se admiten adhesiones si el periodo está cerrado o si pasó
   `fecha_cierre_propuestas`.
10. No se admiten adhesiones de usuarios que no han autorizado el tratamiento de datos.
11. Retirar una adhesión es posible mientras el periodo esté abierto.
12. Las propuestas en estado `RADICADA` o posterior no admiten adhesiones ni retiros.
13. La adhesión, el retiro y el recálculo de estado ocurren dentro de la **misma
    transacción** de base de datos (`transaction.atomic` + `select_for_update` sobre la
    propuesta).

### Estados de la propuesta

14. El quórum se alcanza cuando el número de adhesiones llega a `periodo.cupo_minimo`.
15. Transiciones **automáticas del sistema** (nunca las ejecuta un usuario):
    - `ABIERTA` → `QUORUM` al alcanzar el cupo mínimo
    - `QUORUM` → `ABIERTA` si un retiro deja la propuesta por debajo del cupo
16. Transiciones **manuales del administrador**:
    - `QUORUM` → `RADICADA`
    - `RADICADA` → `APROBADA` o `RECHAZADA`
17. Cualquier otra transición lanza `TransicionInvalidaError`. El administrador no puede
    forzar el paso a `QUORUM`.

### Eliminación de cuenta

18. Si una propuesta apoyada está `ABIERTA` o `QUORUM`, la adhesión se elimina y se
    recalcula el estado, igual que un retiro.
19. Si la propuesta está `RADICADA` o en un estado posterior, la adhesión se conserva y
    los datos personales del usuario se anonimizan.
20. Tras la eliminación, la cuenta no puede volver a iniciar sesión.

### Maestras

21. El borrado de maestras es **lógico** (campo `activa`/`activo`), nunca físico: las
    propuestas históricas deben conservar sus referencias.
22. El código de asignatura es único dentro de un programa, no globalmente: una misma
    asignatura de ciclo básico se registra como un registro independiente por programa,
    con su propio código.

## Proceso de trabajo: TDD obligatorio

Este proyecto se evalúa por el proceso, no solo por el resultado. El historial de Git es
evidencia entregable.

**Ciclo obligatorio para toda lógica de negocio:**

1. Escribir el test que expresa un criterio de aceptación. Nada más.
2. Ejecutarlo y **confirmar que falla por ausencia de la funcionalidad**, no por un error
   de sintaxis o de importación. Si pasa de inmediato, el test está mal.
3. Implementar lo mínimo para que pase.
4. Refactorizar con los tests en verde.

**Prohibido:**

- Escribir implementación sin un test rojo previo.
- Modificar un test para que pase. Si el test está mal, se corrige explicándolo.
- Entregar bloques grandes de código de varias funcionalidades a la vez.
- Usar mocks de la base de datos. Las pruebas corren contra PostgreSQL real.

**Buenos tests:** un solo comportamiento por test; el nombre describe la conducta
esperada (`test_rechaza_adhesion_con_periodo_cerrado`). Si el nombre necesita una "y",
son dos tests.

**Commits:** un commit `test:` y luego un commit `feat:` por cada ciclo.
Ejemplo: `test: rechaza adhesión con periodo cerrado` → `feat: valida periodo cerrado`.

**Al pedir trabajo a Claude Code:** un criterio de aceptación por vez. Si la petición
abarca más de un criterio, dividirla antes de empezar.

**Cobertura:** alta en `propuestas` (reglas y transiciones). En las maestras basta un test
de creación, uno de validación y uno de permisos por entidad. No perseguir cobertura
global alta a costa del tiempo.

**Ejecución:** `uv run pytest`. La opción `--reuse-db` está activa para no recrear la base
de prueba en cada corrida; si cambia el modelo, usar `uv run pytest --create-db`.

**Alcance del ciclo estricto:** el flujo rojo-verde con commits `test:` y `feat:`
separados aplica a la lógica de negocio de `apps/propuestas`. Las maestras, al ser CRUD
sin reglas de dominio propias, se desarrollan con sus pruebas de vistas incluidas en un
único commit `feat:` por entidad. Esta distinción es deliberada y se documenta en el
informe de pruebas.

## Convenciones de código

- Nombres de apps, modelos, campos, variables de dominio y mensajes de usuario en
  **español**. Prefijos de commits y ramas con la convención estándar en inglés
  (`feat/`, `test/`, `chore/`, `docs/`).
- En `apps.py`, el `name` de cada app es la ruta completa: `apps.usuarios`,
  `apps.academico`, etc.
- Vistas basadas en clases. Las cinco maestras comparten vistas y plantillas genéricas:
  se escribe una bien y las demás heredan.
- La lógica de negocio vive en métodos del modelo o en `services.py` de cada app, NUNCA
  en las vistas. Los tests atacan esa capa, no la vista.
- Excepciones de dominio propias (`PeriodoCerradoError`, `AdhesionDuplicadaError`,
  `TransicionInvalidaError`), no `ValidationError` genérico.
- Secretos por variables de entorno con `python-decouple`. El `.env` nunca se sube.
- Fixtures de prueba con `model-bakery`, no con JSON.
- `ruff` para formato y linting antes de cada commit.
- Todo cambio de modelo va acompañado de su archivo de migración en el mismo commit.
- Las vistas genéricas compartidas por las maestras viven en `config/views.py`:
  `ListaConBusquedaView` (búsqueda y filtro por estado, con `campo_activo` configurable
  porque unas entidades usan `activa` y otras `activo`), `DesactivarView` y
  `ReactivarView`, ambas derivadas de `CambiarEstadoView`. Las plantillas compartidas
  están en `templates/componentes/`. Una maestra nueva hereda de ahí, no duplica código.

## Flujo de Git

- Todo trabajo se hace en una rama y entra a `main` mediante pull request.
- Nombres de rama: `feat/maestra-asignaturas`, `test/adhesion-duplicada`,
  `docs/manual-usuario`, `chore/settings`.
- Un pull request no debe esperar más de doce horas sin revisión.
- Claude Code nunca ejecuta `git commit`, `git push` ni `git merge`. Al terminar un
  cambio, resume qué se modificó y el desarrollador hace el commit manualmente.

## Requisitos de la entrega

La aplicación debe tener, y estas son las piezas evaluadas:

- Login y menú con roles (estudiante / administrador)
- **5 pantallas maestras:** facultades-programas, asignaturas, docentes, periodos, usuarios
- **1 pantalla transaccional:** propuesta de curso con adhesiones y máquina de estados
- **2 reportes:** (a) estado de quórum por facultad con porcentaje de avance y días
  restantes; (b) listado de adherentes por propuesta, exportable a PDF
- Publicada y accesible públicamente
- Manual de usuario, manual de instalación y configuración, historias de usuario con
  criterios de aceptación, informe de ejecución de pruebas TDD

Los manuales viven en `docs/` y se escriben en paralelo, no al final.

## Identidad visual

Paleta institucional del Politécnico (manual de identidad gráfica 2025):

    --poli-verde:        #009240   /* marca, encabezado, acción primaria */
    --poli-verde-claro:  #00AB44
    --poli-amarillo:     #FFD400   /* acento, barra de progreso del quórum */
    --poli-teal:         #00A49A   /* informativo, estados secundarios */
    --poli-naranja:      #F97E00

Reglas:

- **Prohibido** el morado `#79067F`: el manual lo reserva para campañas de género.
- Rojo funcional solo para errores y rechazos. Es extensión funcional, no color de marca.
- El logo no se altera: ni colores, ni proporciones, ni posición de elementos. Solo
  versión original, blanco o negro. Área de reserva equivalente al ancho de la "P".
  El nombre Convoca acompaña al logo institucional, nunca lo reemplaza.
- Verificar contraste WCAG 2.1 AA en toda combinación texto-fondo. El verde `#009240`
  sobre blanco NO alcanza 4.5:1, así que no sirve como color de texto pequeño; usar un
  verde oscurecido derivado para texto y enlaces.
- Tipografía institucional Amsi Pro es comercial y no está licenciada para este proyecto.
  Usar alternativa libre y documentarlo en el informe.
- Estilo visualmente limpio. Sin gradientes, sin texturas, sin animaciones de entrada.
  Es una aplicación administrativa, no una landing page.
- Pie de página con nota: proyecto estudiantil, no es un canal oficial de la institución.

## Datos personales

Aplica la Ley 1581 de 2012.

- Recoger el mínimo: nombre, correo institucional y programa. **No pedir cédula ni
  código estudiantil.**
- En la vista pública de una propuesta se muestran solo nombre y programa de los
  adherentes. Nunca el correo.
- El listado de adherentes solo es visible para usuarios autenticados.
- El PDF de adherentes incluye nombre y programa, nunca correo.
- El administrador puede ver nombre, correo, programa y estado de autorización de los
  usuarios, y desactivar o reactivar cuentas. Nunca ve ni modifica contraseñas.
- El usuario puede retirar su adhesión y eliminar su cuenta (ver reglas 18 a 20).

## Fuera de alcance

No implementar: integración con Universitas XXI, pagos, notificaciones por correo,
aplicación móvil, carga masiva de asignaturas desde archivos, ni Neon Auth u otros
servicios de Neon distintos a la base de datos. Si algo de esto parece necesario,
preguntar antes de implementarlo.