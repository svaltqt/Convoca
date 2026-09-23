# Manual de instalación y configuración

**Producto:** Plataforma de cursos vacacionales — Politécnico Colombiano Jaime Isaza Cadavid
**Versión del documento:** 1.0
**Versión de la aplicación:** [x.y.z]
**Fecha:** [fecha]
**Autores:** [nombres del grupo]

---

## Tabla de contenido

1. Introducción
2. Requisitos
3. Obtención del código
4. Configuración del entorno
5. Base de datos
6. Datos de demostración
7. Ejecución local
8. Verificación de la instalación
9. Ejecución de las pruebas
10. Despliegue en producción
11. Solución de problemas
12. Mantenimiento

---

## 1. Introducción

### 1.1 Propósito

Describe el procedimiento para instalar, configurar, ejecutar y desplegar la aplicación,
tanto en un entorno local de desarrollo como en producción.

### 1.2 Audiencia

Personal técnico con conocimientos básicos de línea de comandos, Git y bases de datos
relacionales. No requiere conocimiento previo del proyecto.

### 1.3 Arquitectura general

Aplicación web construida con Django, servida por Gunicorn, con base de datos
PostgreSQL. Las plantillas se renderizan en el servidor y la interactividad se resuelve
con HTMX. No requiere Node.js ni proceso de compilación de recursos.

    Navegador → Gunicorn/WhiteNoise → Django → PostgreSQL

---

## 2. Requisitos

### 2.1 Software

| Componente | Versión mínima | Notas |
|---|---|---|
| Python | 3.12 | |
| PostgreSQL | 14 | Local o servicio gestionado |
| Git | 2.x | |
| uv | [versión] | Gestor de dependencias |

### 2.2 Hardware

Para desarrollo local: 4 GB de RAM y 2 GB de espacio libre en disco.

### 2.3 Cuentas y servicios externos

- Repositorio en GitHub
- Cuenta en Neon (base de datos en producción)
- Cuenta en Render (alojamiento de la aplicación)

---

## 3. Obtención del código

```bash
git clone [url del repositorio]
cd vacacionales
```

---

## 4. Configuración del entorno

### 4.1 Instalación de dependencias

```bash
uv sync
```

### 4.2 Variables de entorno

Copie el archivo de ejemplo y edítelo:

```bash
cp .env.example .env
```

| Variable | Descripción | Ejemplo | Obligatoria |
|---|---|---|---|
| `SECRET_KEY` | Clave criptográfica de Django | `django-insecure-...` | Sí |
| `DEBUG` | Modo depuración. `False` en producción | `True` | Sí |
| `DATABASE_URL` | Cadena de conexión a PostgreSQL | `postgres://usuario:clave@localhost:5432/vacacionales` | Sí |
| `ALLOWED_HOSTS` | Dominios permitidos, separados por coma | `localhost,127.0.0.1` | Sí |
| `DJANGO_SETTINGS_MODULE` | Módulo de configuración | `config.settings.local` | Sí |
| [otras] | | | |

> **Advertencia:** el archivo `.env` nunca debe subirse al repositorio. Ya está incluido
> en `.gitignore`.

---

## 5. Base de datos

### 5.1 Creación

```bash
createdb vacacionales
```

### 5.2 Migraciones

```bash
uv run python manage.py migrate
```

### 5.3 Usuario administrador

```bash
uv run python manage.py createsuperuser
```

---

## 6. Datos de demostración

Carga catálogos y propuestas de ejemplo en distintos estados:

```bash
uv run python manage.py seed_demo
```

> **Advertencia:** este comando elimina los datos existentes antes de cargar. No ejecutar
> sobre una base de datos con información real.

---

## 7. Ejecución local

```bash
uv run python manage.py runserver
```

La aplicación queda disponible en `http://127.0.0.1:8000`.

---

## 8. Verificación de la instalación

Confirme que la instalación es correcta comprobando los siguientes puntos:

| # | Acción | Resultado esperado |
|---|---|---|
| 1 | Abrir `http://127.0.0.1:8000` | Se muestra la pantalla de inicio de sesión |
| 2 | Iniciar sesión con el superusuario | Se muestra el menú con la opción Administración |
| 3 | Entrar a `Propuestas` | Se listan las propuestas cargadas por el seeder |
| 4 | Entrar a `Reportes > Estado de quórum` | Se muestran datos agregados por facultad |
| 5 | Generar el PDF de interesados | Se descarga un archivo PDF legible |

Si alguno falla, consulte la sección 11.

---

## 9. Ejecución de las pruebas

```bash
uv run pytest
```

Genera dos artefactos:

- `docs/informe-pruebas.html` — informe de ejecución
- `htmlcov/index.html` — reporte de cobertura

Para ejecutar solo las pruebas de un módulo:

```bash
uv run pytest apps/propuestas
```

---

## 10. Despliegue en producción

### 10.1 Base de datos en Neon

1. Cree un proyecto y una base de datos.
2. Copie la cadena de conexión, usando el punto de conexión con agrupación (pooler).

### 10.2 Servicio web en Render

1. Cree un servicio web conectado al repositorio.
2. Configure comando de construcción y comando de inicio:

```
Build:  uv sync && uv run python manage.py collectstatic --noinput && uv run python manage.py migrate
Start:  uv run gunicorn config.wsgi:application
```

3. Registre las variables de entorno, con `DEBUG=False`,
   `DJANGO_SETTINGS_MODULE=config.settings.production` y el dominio en `ALLOWED_HOSTS`.

### 10.3 Consideraciones

- Los archivos estáticos se sirven con WhiteNoise; no requiere almacenamiento externo.
- Use `CONN_MAX_AGE = 0` o el pooler de Neon para no agotar las conexiones disponibles.
- En el plan gratuito de Render el servicio se suspende por inactividad y la primera
  petición puede tardar cerca de un minuto.

---

## 11. Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `django.db.utils.OperationalError` al migrar | PostgreSQL no está en ejecución o `DATABASE_URL` es incorrecta | Verifique el servicio y la cadena de conexión |
| Los estilos no cargan en producción | No se ejecutó `collectstatic` | Revise el comando de construcción |
| `DisallowedHost` | El dominio no está en `ALLOWED_HOSTS` | Agregue el dominio y reinicie |
| `too many connections` | Agotamiento de conexiones de la base de datos | Configure `CONN_MAX_AGE` o use el pooler |
| Las pruebas fallan por permisos de base de datos | El usuario no puede crear bases de datos de prueba | Otorgue el permiso `CREATEDB` |
| [otros] | | |

---

## 12. Mantenimiento

### 12.1 Respaldo de la base de datos

```bash
pg_dump [cadena de conexión] > respaldo_$(date +%F).sql
```

### 12.2 Actualización de dependencias

```bash
uv lock --upgrade
uv sync
uv run pytest
```

Ejecute siempre la suite de pruebas después de actualizar.

### 12.3 Aplicación de cambios

```bash
git pull
uv sync
uv run python manage.py migrate
```
