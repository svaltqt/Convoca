# CLAUDE.md — Vacacionales Poli JIC

## Contexto del proyecto

Aplicación web que permite a estudiantes del Politécnico Colombiano Jaime Isaza Cadavid
**proponer cursos vacacionales y reunir el quórum mínimo de 20 estudiantes** antes de la
inscripción oficial.

Hoy ese proceso ocurre por voz a voz y grupos de WhatsApp. No existe plataforma para ver
qué cursos están reuniendo gente.

**Límite de alcance (crítico):** esta aplicación NO matricula ni inscribe. Registra
intención de matrícula. La inscripción oficial sigue siendo por Universitas XXI en la
fecha del calendario académico. Toda la UI debe reflejar esto: usar "interesados",
"apoyar propuesta", "me interesa". NUNCA "inscritos" ni "inscribirme".

Entrega académica. Fecha límite: 26 de septiembre de 2026.

## Stack

- Python 3.12+, Django 5.2 LTS
- PostgreSQL (psycopg), sin SQLite ni siquiera en pruebas
- Plantillas de Django + HTMX + CSS propio. **Sin React, sin Node, sin build step**
- pytest + pytest-django + pytest-cov + pytest-html + model-bakery
- WeasyPrint para reportes PDF
- Gunicorn + WhiteNoise, desplegado en Render con BD en Neon
- Gestión de dependencias con `uv`

## Modelo de datos

    Facultad 1─n Programa 1─n Asignatura
    Asignatura 1─n Propuesta n─1 Periodo
    Docente 1─n Propuesta (sugerido, opcional)
    Usuario 1─n Propuesta (creador)
    Propuesta 1─n Adhesion n─1 Usuario

Apps: `usuarios`, `academico` (facultad, programa, asignatura, docente), `periodos`,
`propuestas` (propuesta, adhesion), `reportes`.

Campos clave:

- `Periodo`: nombre, fecha_cierre_propuestas, cupo_minimo (default 20), abierto
- `Asignatura`: codigo, nombre, creditos, programa, activa
- `Propuesta`: asignatura, periodo, creador, estado, creada
- `Adhesion`: propuesta, usuario, creada
- `Usuario`: modelo personalizado (`AUTH_USER_MODEL`), codigo_estudiantil, email
  institucional, autorizo_datos, fecha_autorizacion

## Reglas de negocio

Estas son la fuente de verdad. Si el código contradice esta sección, el código está mal.

1. Un usuario puede adherirse **una sola vez** a una propuesta. Restricción única en BD
   `(propuesta, usuario)`, no solo validación en el formulario.
2. No se admiten adhesiones si el periodo está cerrado o si pasó `fecha_cierre_propuestas`.
3. No se admiten adhesiones de usuarios que no han autorizado el tratamiento de datos.
4. No puede existir más de una propuesta activa para la misma `(asignatura, periodo)`.
5. El quórum se alcanza cuando el número de adhesiones llega a `periodo.cupo_minimo`.
6. Retirar una adhesión es posible mientras el periodo esté abierto, y puede devolver la
   propuesta de "quórum alcanzado" a "abierta".
7. Estados de `Propuesta` y transiciones válidas:
   - `ABIERTA` → `QUORUM` (al alcanzar el cupo mínimo)
   - `QUORUM` → `ABIERTA` (si se retiran adhesiones y baja del cupo)
   - `QUORUM` → `RADICADA` (acción de administrador)
   - `RADICADA` → `APROBADA` | `RECHAZADA` (acción de administrador)
   - Cualquier otra transición lanza `TransicionInvalidaError`
8. Las propuestas en estado `RADICADA` o posterior no admiten adhesiones ni retiros.
9. El borrado de maestras es **lógico** (campo `activa`), nunca físico: las propuestas
   históricas deben conservar sus referencias.
10. La adhesión y el recálculo de estado ocurren dentro de la **misma transacción**
    de base de datos (`transaction.atomic` + `select_for_update` sobre la propuesta).

## Proceso de trabajo: TDD obligatorio

Este proyecto se evalúa por el proceso, no solo por el resultado. El historial de Git es
evidencia entregable.

**Ciclo obligatorio para toda lógica de negocio:**

1. Escribir el test que expresa un criterio de aceptación. Nada más.
2. Ejecutarlo y verlo fallar.
3. Implementar lo mínimo para que pase.
4. Refactorizar con los tests en verde.

**Prohibido:**

- Escribir implementación sin un test rojo previo.
- Modificar un test para que pase. Si el test está mal, se corrige explicándolo.
- Entregar bloques grandes de código de varias funcionalidades a la vez.

**Commits:** un commit `test:` y luego un commit `feat:` por cada ciclo.
Ejemplo: `test: rechaza adhesión con periodo cerrado` → `feat: valida periodo cerrado`.

**Al pedir trabajo a Claude Code:** un criterio de aceptación por vez. Si la petición
abarca más de un criterio, dividirla antes de empezar.

**Cobertura:** alta en `propuestas` (reglas y transiciones). En las maestras basta un test
de creación, uno de validación y uno de permisos por entidad. No perseguir cobertura
global alta a costa del tiempo.

## Convenciones de código

- Vistas basadas en clases. Las cinco maestras comparten vistas y plantillas genéricas:
  se escribe una bien y las demás heredan.
- La lógica de negocio vive en métodos del modelo o en `services.py` de cada app, NUNCA
  en las vistas. Los tests atacan esa capa, no la vista.
- Excepciones de dominio propias (`PeriodoCerradoError`, `AdhesionDuplicadaError`,
  `TransicionInvalidaError`), no `ValidationError` genérico.
- `settings/` dividido en `base.py`, `local.py`, `production.py`. Secretos por variables
  de entorno con `python-decouple`. El `.env` nunca se sube.
- Fixtures de prueba con `model-bakery`, no con JSON.
- `ruff` para formato y linting antes de cada commit.
- Nombres de modelos, campos y mensajes de usuario en español. Código y ramas en inglés.

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
- Verificar contraste WCAG AA en toda combinación texto-fondo. El verde `#009240` sobre
  blanco NO alcanza 4.5:1, así que no sirve como color de texto pequeño; usar un verde
  oscurecido derivado para texto y enlaces.
- Tipografía institucional Amsi Pro es comercial y no está licenciada para este proyecto.
  Usar alternativa libre y documentarlo en el informe.
- Estilo visualmente limpio. Sin gradientes, sin texturas, sin animaciones de entrada.
  Es una aplicación administrativa, no una landing page.
- Pie de página con nota: proyecto estudiantil, no es un canal oficial de la institución.

## Datos personales

Aplica la Ley 1581 de 2012.

- Recoger el mínimo: nombre, código estudiantil, correo institucional, programa.
  **No pedir cédula.**
- Autorización expresa en el registro, casilla sin marcar por defecto, con enlace a la
  política de tratamiento. Guardar fecha y hora de la autorización.
- En la vista pública de una propuesta se muestran solo nombre y programa de los
  adherentes. Nunca correo ni código.
- El usuario puede retirar su adhesión y eliminar su cuenta.

## Fuera de alcance

No implementar: integración con Universitas XXI, pagos, notificaciones por correo,
aplicación móvil, ni carga masiva de asignaturas desde archivos. Si algo de esto parece
necesario, preguntar antes de implementarlo.
