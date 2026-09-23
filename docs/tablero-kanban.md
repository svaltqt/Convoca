# Tablero de tareas — Convoca

**Entrega:** 26 de septiembre de 2026
**Equipo:** A (infraestructura y maestras) · B (transaccional) · C (reportes y frontend) · D (QA y documentación)

Estado: ✅ terminado · 🔄 en curso · ⬜ pendiente

---

## Definición de terminado

Una tarea se considera terminada solo si cumple los cinco puntos:

- [ ] Tiene pruebas que cubren sus criterios de aceptación
- [ ] La suite completa pasa en verde
- [ ] El código está fusionado en `main`
- [ ] El despliegue público está actualizado
- [ ] La sección correspondiente del manual está redactada

**Límite de trabajo en curso: una tarea por persona.**

---

## Sprint 0 — Preparación

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 0.1 | Cerrar modelo de datos y estados | Todos | 🔄 Faltan dos decisiones del grupo |
| 0.2 | Repositorio, ramas y política de PR | A | 🔄 Falta proteger `main` |
| 0.3 | Esqueleto Django, apps y dependencias | A | ✅ |
| 0.4 | Modelo de usuario personalizado | A | ✅ |
| 0.5 | Settings divididos y variables de entorno | A | ✅ |
| 0.6 | Proyecto en Neon con ramas por integrante | A | ✅ |
| 0.7 | Despliegue en Render | A | ✅ |
| 0.8 | pytest con cobertura e informe HTML | A | ✅ |
| 0.9 | Integración continua en GitHub Actions | A | ✅ |
| 0.10 | Historias de usuario con criterios | D | ✅ |
| 0.11 | Manuales en `docs/` | D | ⬜ Falta subirlos y actualizarlos |
| 0.12 | Modelos de las maestras | A | ✅ |
| 0.13 | Comando `seed_demo` | A | ✅ |
| 0.14 | Registro de modelos en el admin | A | ✅ |
| 0.15 | Sistema visual: `base.html` y componentes | A | ✅ |

**Decisiones pendientes de 0.1:** si una asignatura puede pertenecer a varios programas
(resuelto como registros independientes por programa), y si existe un estado de vencida
para propuestas que no alcanzan el quórum a tiempo.

---

## Sprint 1 — Base navegable

### Autenticación y menú

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 1.1 | Registro con autorización de datos | A | ✅ |
| 1.2 | Inicio y cierre de sesión | A | ✅ |
| 1.3 | Roles y permisos con grupos | A | ⬜ |
| 1.4 | Menú condicionado por rol | A | 🔄 Usa `is_staff`, migrar a grupos |
| 1.5 | Página de política de tratamiento | A | ✅ |
| 1.6 | Perfil y eliminación de cuenta | A | ⬜ |

### Maestras

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 1.7 | Facultades y programas | A | ✅ |
| 1.8 | Asignaturas | | ⬜ |
| 1.9 | Docentes | | ⬜ |
| 1.10 | Periodos vacacionales | | ⬜ |
| 1.11 | Usuarios | | ⬜ |
| 1.12 | Búsqueda, filtros y paginación | A | ✅ En vistas genéricas |
| 1.13 | Borrado lógico con reactivación | A | ✅ |

### Transversal

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 1.14 | Modelos de propuesta y adhesión | A | ✅ |
| 1.15 | Excepciones de dominio | B | ⬜ |
| 1.16 | Validar adhesión duplicada (TDD) | B | ⬜ |
| 1.17 | Validar periodo cerrado (TDD) | B | ⬜ |
| 1.18 | Validar autorización de datos (TDD) | B | ⬜ |
| 1.19 | Diseño de plantilla base y componentes | A | ✅ |
| 1.20 | Manual de usuario: registro, login y menú | D | ⬜ |
| 1.21 | Manual de instalación: secciones 1 a 7 | D | ⬜ |
| 1.22 | Revisar cobertura de las maestras | D | ✅ 98% |

---

## Sprint 2 — Transaccional y reportes

### Transaccional

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 2.1 | Crear propuesta sin duplicados (TDD) | B | ⬜ |
| 2.2 | Cálculo de quórum y transición (TDD) | B | ⬜ |
| 2.3 | Retiro de adhesión (TDD) | B | ⬜ |
| 2.4 | Transiciones de estado válidas (TDD) | B | ⬜ |
| 2.5 | Bloqueo en propuestas radicadas (TDD) | B | ⬜ |
| 2.6 | Transacción atómica con bloqueo de fila | B | ⬜ |
| 2.7 | Detalle de propuesta con barra de quórum | C | ⬜ |
| 2.8 | Listado de propuestas con filtros | C | ⬜ |
| 2.9 | Pantalla "Mis apoyos" | C | ⬜ |
| 2.10 | Acciones de administrador sobre propuestas | B | ⬜ |

### Reportes

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 2.11 | Reporte de quórum por facultad | C | ⬜ |
| 2.12 | Reporte de interesados por propuesta | C | ⬜ |
| 2.13 | Exportación a PDF con WeasyPrint | C | ⬜ |
| 2.14 | Pruebas de los reportes | C | ⬜ |

### Documentación

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 2.15 | Manual de usuario: tareas del estudiante | D | ⬜ |
| 2.16 | Manual de usuario: tareas del administrador | D | ⬜ |
| 2.17 | Manual de usuario: errores y glosario | D | ⬜ |
| 2.18 | Manual de instalación: despliegue y problemas | D | ⬜ |
| 2.19 | Informe de pruebas TDD | D | ⬜ |
| 2.20 | Trazabilidad historias ↔ pruebas ↔ manual | D | ⬜ |

### Cierre técnico

| # | Tarea | Resp. | Estado |
|---|---|---|---|
| 2.21 | Verificar contraste y accesibilidad | C | 🔄 Medido en componentes |
| 2.22 | Pie con aviso de proyecto no oficial | A | ✅ |
| 2.23 | Despliegue final con datos de demostración | A | ⬜ |
| 2.24 | Plantillas de error 403 y 404 con el diseño | | ⬜ |

---

## Viernes 25 — Congelamiento

**Cero código nuevo.**

| # | Tarea | Resp. |
|---|---|---|
| 3.1 | Pruebas exploratorias intentando romper la aplicación | D |
| 3.2 | Corrección únicamente de defectos críticos | B |
| 3.3 | Informe final de pruebas y cobertura | D |
| 3.4 | Revisión de manuales en una máquina limpia | D |
| 3.5 | Verificar la URL pública con datos correctos | A |
| 3.6 | Ensayo de la sustentación | Todos |
| 3.7 | Empaquetar entregables | D |

---

## Plan de recorte si hay atraso

En este orden, decidido de antemano:

1. Simplificar el pulido visual (2.21 al mínimo)
2. Reducir el reporte de interesados a su versión más simple
3. Eliminar la pantalla "Mis apoyos" (2.9)
4. Quitar el perfil y la eliminación de cuenta (1.6)

**Nunca se recorta:** despliegue público, informe TDD, manuales, ni la transaccional.

---

## Limitaciones reconocidas

Para documentar en el informe, no para resolver:

- Una asignatura pertenece a un solo programa. Las materias de ciclo básico compartidas
  entre ingenierías se representan como registros independientes por programa, cada uno
  con su código. Esto implica que dos grupos del mismo curso compiten por quórum por
  separado.
- La plataforma no valida prerrequisitos ni el programa del estudiante frente al de la
  asignatura: mide intención, no elegibilidad.
- La conversión de interés a matrícula es imperfecta; el conteo de interesados es una
  estimación optimista del número de matriculados reales.
