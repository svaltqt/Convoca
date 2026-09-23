# PRD — Convoca

**Producto:** Convoca — plataforma de intención de matrícula para cursos vacacionales
**Institución:** Politécnico Colombiano Jaime Isaza Cadavid
**Tipo de entrega:** Proyecto académico (TDD obligatorio, historial de Git como evidencia)
**Fecha límite de entrega:** 26 de septiembre de 2026
**Fuente de las historias de usuario:** `docs/Historias de usuario - Desarrollo.pdf`
**Fuente de las reglas de negocio y restricciones técnicas:** `CLAUDE.md` (raíz del repositorio)

---

## 1. Resumen ejecutivo

Convoca es una aplicación web que permite a los estudiantes del Politécnico Colombiano
Jaime Isaza Cadavid **proponer cursos vacacionales** y **reunir el quórum mínimo de
interesados** antes de que se abra la inscripción oficial. Hoy ese proceso ocurre de
manera informal, por voz a voz y grupos de WhatsApp, sin ningún lugar donde consultar
qué cursos están reuniendo gente.

Convoca no reemplaza ni interviene en el proceso de matrícula: **registra intención**,
no inscribe. La matrícula oficial sigue haciéndose por Universitas XXI, en las fechas
del calendario académico.

## 2. Problema y contexto

- Los estudiantes interesados en un curso vacacional no tienen visibilidad de cuántos
  compañeros comparten ese interés, ni de qué tan cerca está un curso de alcanzar el
  cupo mínimo para abrirse.
- La coordinación actual (WhatsApp, voz a voz) no deja rastro, se pierde entre
  semestres y no informa a los administradores académicos del avance real de la
  demanda.
- No existe un canal para que los administradores vean, por facultad, qué propuestas
  están cerca del quórum y puedan radicarlas a tiempo para el proceso de matrícula.

## 3. Objetivo del producto

Dar a estudiantes y administradores un lugar único donde:

1. Un estudiante pueda **proponer** un curso vacacional sobre una asignatura y periodo
   concretos, y **apoyar** propuestas de otros estudiantes.
2. Cualquiera pueda ver, en tiempo real, cuántos interesados tiene una propuesta y qué
   tan cerca está del cupo mínimo.
3. Un administrador pueda **gestionar las maestras académicas** (facultades,
   programas, asignaturas, docentes, periodos) y **avanzar el estado de una propuesta**
   una vez alcanza el quórum, hasta radicarla y aprobarla o rechazarla.
4. La institución reciba, al final, un listado confiable de qué cursos tienen demanda
   suficiente para considerarse en el proceso oficial de matrícula — sin que Convoca
   sea quien matricula.

**No son objetivos de este producto:** integrarse con Universitas XXI, procesar pagos,
enviar notificaciones por correo, ofrecer una app móvil, o sustituir cualquier sistema
oficial de la institución.

## 4. Usuarios y roles

| Rol | Quién es | Qué puede hacer |
|---|---|---|
| **Estudiante** | Cualquier persona con correo institucional que se registra en la plataforma | Proponer cursos, apoyar y retirar su apoyo a propuestas, ver el avance del quórum, eliminar su propia cuenta |
| **Administrador** | Personal autorizado (`is_staff`) | Todo lo anterior salvo proponer/adherirse, más: gestionar las maestras académicas, radicar/aprobar/rechazar propuestas, consultar reportes y usuarios, exportar adherentes a PDF |

El sistema identifica el rol al autenticarse y solo expone las funcionalidades
correspondientes a ese rol (RF-01).

## 5. Alcance

### 5.1 Dentro del alcance

- Autenticación y registro con correo institucional (dominio configurable).
- Autorización expresa y trazable de tratamiento de datos personales (Ley 1581 de
  2012).
- Cinco pantallas maestras: facultades y programas, asignaturas, docentes, periodos,
  usuarios — con borrado lógico, nunca físico.
- Una pantalla transaccional: propuesta de curso con adhesiones y máquina de estados.
- Dos reportes: estado de quórum por facultad (con porcentaje de avance y días
  restantes) y listado de adherentes por propuesta, exportable a PDF.
- Eliminación de cuenta por parte del propio usuario, con anonimización cuando la
  propuesta ya fue radicada.
- Publicación pública de la aplicación en un servidor accesible por URL.

### 5.2 Fuera de alcance

No se implementa, y si en algún momento parece necesario se debe preguntar antes de
construirlo:

- Integración con Universitas XXI o cualquier otro sistema oficial de matrícula.
- Pagos.
- Notificaciones por correo electrónico.
- Aplicación móvil.
- Carga masiva de asignaturas desde archivos.
- Neon Auth u otros servicios de Neon distintos a la base de datos.

## 6. Historias de usuario

Prioridad tal como está definida en `docs/Historias de usuario - Desarrollo.pdf`.

| ID | Historia | Rol | Prioridad |
|---|---|---|---|
| HU-01 | Autenticación de usuario | Estudiante / Administrador | Alta |
| HU-02 | Registro de estudiante | Estudiante | Media |
| HU-03 | Gestionar facultades y programas | Administrador | Media |
| HU-04 | Gestionar asignaturas | Administrador | Media |
| HU-05 | Gestionar docentes | Administrador | Baja |
| HU-06 | Gestionar periodos académicos | Administrador | Media |
| HU-07 | Gestionar usuarios | Administrador | Media |
| HU-08 | Proponer un curso vacacional | Estudiante | Alta |
| HU-09 | Consultar propuestas | Estudiante | Alta |
| HU-10 | Apoyar una propuesta | Estudiante | Alta |
| HU-11 | Alcanzar el quórum | Estudiante / Sistema | Alta |
| HU-12 | Retirar una adhesión | Estudiante | Alta |
| HU-13 | Gestionar el estado de una propuesta | Administrador | Alta |
| HU-14 | Consultar adherentes de una propuesta | Usuario autorizado | Baja |
| HU-15 | Consultar reporte de quórum | Administrador | Media |
| HU-16 | Exportar adherentes a PDF | Administrador | Media |
| HU-17 | Eliminar mi cuenta | Estudiante | Media |
| HU-18 | Dejar claro el alcance de la plataforma | Estudiante | Baja |

Los criterios de aceptación completos de cada historia están en el PDF fuente; cada
test de lógica de negocio del proyecto debe poder señalar a uno de esos criterios.

## 7. Requisitos funcionales

| ID | Nombre | Actor | Historia |
|---|---|---|---|
| RF-01 | Autenticación y roles | Estudiante / Administrador | HU-01 |
| RF-02 | Registro de estudiantes | Estudiante | HU-02 |
| RF-03 | Autorización de tratamiento de datos | Estudiante | HU-02 |
| RF-04 | Gestión de facultades y programas | Administrador | HU-03 |
| RF-05 | Gestión de asignaturas | Administrador | HU-04 |
| RF-06 | Gestión de docentes | Administrador | HU-05 |
| RF-07 | Gestión de periodos académicos | Administrador | HU-06 |
| RF-08 | Gestión de usuarios | Administrador | HU-07 |
| RF-09 | Creación de propuestas | Estudiante | HU-08 |
| RF-10 | Validación de propuestas (unicidad por asignatura/periodo) | Sistema | HU-08 |
| RF-11 | Consulta de propuestas | Estudiante / Administrador | HU-09 |
| RF-12 | Adhesión a propuestas | Estudiante | HU-10 |
| RF-13 | Validación de adhesiones (duplicadas, periodo cerrado, sin autorización) | Sistema | HU-10 |
| RF-14 | Cálculo y actualización automática del quórum | Sistema | HU-11 / HU-12 |
| RF-15 | Retiro de adhesiones | Estudiante | HU-12 |
| RF-16 | Recuperación del estado ABIERTA al perder el quórum | Sistema | HU-12 |
| RF-17 | Máquina de estados de propuestas | Sistema / Administrador | HU-13 |
| RF-18 | Gestión administrativa de propuestas (radicar, aprobar, rechazar) | Administrador | HU-13 |
| RF-19 | Consulta de adherentes (nombre y programa, nunca correo) | Estudiante / Administrador | HU-14 |
| RF-20 | Protección de datos personales de los adherentes | Sistema | HU-14 |
| RF-21 | Reporte de quórum por facultad | Administrador | HU-15 |
| RF-22 | Reporte de adherentes por propuesta | Administrador | HU-16 |
| RF-23 | Exportación de reportes a PDF | Administrador | HU-16 |
| RF-24 | Eliminación de cuenta (con anonimización condicional) | Estudiante | HU-17 |
| RF-25 | Información explícita sobre el alcance de la plataforma | Estudiante | HU-18 |

## 8. Requisitos no funcionales

| ID | Nombre | Categoría | Descripción | Verificación |
|---|---|---|---|---|
| RNF-01 | Disponibilidad pública | Disponibilidad | La aplicación debe estar publicada y ser accesible por una URL pública | Acceso desde un navegador externo a la red del equipo |
| RNF-02 | Protección de datos personales | Legal | Cumplimiento de la Ley 1581 de 2012: autorización expresa, finalidad declarada, recolección mínima, derecho de supresión | Revisión de la política de tratamiento, el formulario de registro y la eliminación de cuenta |
| RNF-03 | Almacenamiento seguro de contraseñas | Seguridad | Las contraseñas se almacenan cifradas (hash), nunca en texto plano | Inspección de la tabla de usuarios en la base de datos |
| RNF-04 | Accesibilidad | Usabilidad | Contraste mínimo WCAG 2.1 AA en toda combinación texto/fondo; navegación posible por teclado | Medición de contraste y recorrido con teclado de las pantallas principales |
| RNF-05 | Identidad visual institucional | Usabilidad | Respeto de la paleta y reglas de uso del logosímbolo del Manual de Identidad Gráfica del Politécnico | Contraste de colores y uso del logo contra el manual |
| RNF-06 | Calidad del software | Mantenibilidad | La lógica de negocio se desarrolla con TDD y pruebas automatizadas que corren en cada cambio | Informe de ejecución de pruebas, reporte de cobertura e historial de integración continua |

## 9. Modelo de datos

```
Facultad 1─n Programa 1─n Asignatura
Asignatura 1─n Propuesta n─1 Periodo
Docente 1─n Propuesta (sugerido, opcional)
Usuario 1─n Propuesta (creador)
Propuesta 1─n Adhesion n─1 Usuario
Programa 1─n Usuario
```

Apps: `usuarios`, `academico` (facultad, programa, asignatura, docente), `periodos`,
`propuestas` (propuesta, adhesion), `reportes`.

Campos y restricciones relevantes (ver `CLAUDE.md` para el detalle completo):

- **Usuario**: se identifica por correo institucional (`USERNAME_FIELD = "email"`), sin
  campo de nombre de usuario. No almacena código estudiantil ni cédula.
- **Periodo**: `cupo_minimo` con valor predeterminado 20, `fecha_cierre_propuestas`,
  `abierto`.
- **Propuesta**: única por `(asignatura, periodo)` mientras esté en cualquier estado
  distinto de `RECHAZADA`.
- Todas las maestras usan borrado lógico (`activa`/`activo`), nunca físico, para que
  las propuestas históricas conserven sus referencias.

## 10. Reglas de negocio clave

**Máquina de estados de `Propuesta`:**

```
ABIERTA ──(alcanza cupo_minimo)──> QUORUM
QUORUM ──(retiro deja por debajo del cupo)──> ABIERTA
QUORUM ──(acción del administrador)──> RADICADA
RADICADA ──(acción del administrador)──> APROBADA | RECHAZADA
```

- Las transiciones `ABIERTA ⇄ QUORUM` son automáticas y las ejecuta el sistema; las
  transiciones desde `QUORUM` en adelante son manuales y las ejecuta un administrador.
  Cualquier otra transición lanza un error de transición inválida.
- Toda propuesta nueva empieza en `ABIERTA` y quien la crea queda automáticamente
  adherido a ella.
- Una adhesión, un retiro y el recálculo de estado ocurren dentro de la misma
  transacción de base de datos.
- No se admiten adhesiones ni retiros si el periodo está cerrado, si venció
  `fecha_cierre_propuestas`, o si la propuesta está en `RADICADA` o un estado
  posterior.
- Un usuario no puede adherirse dos veces a la misma propuesta (restricción única en
  base de datos, no solo validación de formulario).
- Al eliminar una cuenta: si la propuesta apoyada está `ABIERTA` o `QUORUM`, la
  adhesión se borra y se recalcula el estado; si está `RADICADA` o posterior, la
  adhesión se conserva y los datos personales del usuario se anonimizan. Tras
  eliminarla, la cuenta no puede volver a iniciar sesión.

## 11. Identidad visual y accesibilidad

- Paleta institucional fija (verde `#009240`, amarillo `#FFD400`, teal `#00A49A`,
  naranja `#F97E00`), con un verde oscurecido derivado para texto y enlaces porque el
  verde de marca no alcanza el contraste AA sobre blanco. El morado `#79067F` está
  prohibido (reservado por el manual institucional para campañas de género); el rojo
  funcional se usa solo para errores y rechazos.
- Toda combinación de texto y fondo debe alcanzar 4.5:1 de contraste (WCAG 2.1 AA).
- El logo institucional no se altera; el nombre "Convoca" lo acompaña, nunca lo
  reemplaza.
- Estilo administrativo, sin gradientes, texturas ni animaciones de entrada.

## 12. Datos personales y cumplimiento legal (Ley 1581 de 2012)

- Recolección mínima: nombre, correo institucional y programa. Nunca cédula ni código
  estudiantil.
- La vista pública de una propuesta muestra solo nombre y programa de los adherentes;
  el correo nunca se expone. El listado de adherentes solo es visible para usuarios
  autenticados.
- El PDF de adherentes incluye nombre y programa, nunca correo.
- El administrador puede ver nombre, correo, programa y estado de autorización de los
  usuarios, y desactivar o reactivar cuentas — nunca ve ni modifica contraseñas.
- El usuario puede retirar su adhesión y eliminar su cuenta en cualquier momento.

## 13. Stack tecnológico y despliegue

- Python 3.12+, Django 6.1.
- PostgreSQL en Neon (rama `production` solo para Render; cada integrante trabaja
  sobre su propia rama de desarrollo).
- Django templates + HTMX, sin React ni build step.
- pytest + pytest-django + model-bakery, corriendo contra PostgreSQL real (sin mocks
  de base de datos).
- WeasyPrint para los reportes en PDF.
- Gunicorn + WhiteNoise, desplegado en Render (región Ohio).

## 14. Entregables de la evaluación

- Login y menú con roles (estudiante / administrador).
- Cinco pantallas maestras y una pantalla transaccional (propuesta + adhesiones +
  máquina de estados).
- Dos reportes (quórum por facultad; adherentes por propuesta, exportable a PDF).
- Aplicación publicada y accesible públicamente.
- Manual de usuario, manual de instalación y configuración, historias de usuario con
  criterios de aceptación, e informe de ejecución de pruebas TDD.

## 15. Riesgos y supuestos

- **Riesgo:** confundir "adhesión" con "matrícula" en la interfaz induciría a error a
  los estudiantes. *Mitigación:* vocabulario controlado ("interesados", "apoyar
  propuesta") reforzado en HU-18 / RF-25 y en el pie de página de toda la aplicación.
- **Riesgo:** el verde institucional no cumple AA como color de texto sobre blanco.
  *Mitigación:* uso de un verde oscurecido derivado, documentado en el sistema de
  diseño (`static/css/estilos.css`).
- **Supuesto:** el rol de administrador se resuelve con `is_staff` de Django; el
  proyecto no define un modelo de roles más granular porque no hay una historia de
  usuario que lo requiera.
- **Riesgo:** al ser un proyecto académico con fecha límite fija (2026-09-26), la
  prioridad "Baja" de HU-05, HU-14 y HU-18 es la primera candidata a recortarse si el
  tiempo se agota; ninguna de las tres bloquea el flujo principal de propuestas.

## 16. Referencias

- `CLAUDE.md` — reglas de negocio, modelo de datos, convenciones de código e
  identidad visual, fuente de la verdad cuando hay contradicción con este documento.
- `docs/Historias de usuario - Desarrollo.pdf` — historias de usuario y criterios de
  aceptación completos.
- `docs/informe-pruebas.html` — informe de ejecución de pruebas (se regenera con cada
  corrida de `pytest`).
