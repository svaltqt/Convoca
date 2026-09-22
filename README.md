Readme · MD
# Convoca
 
Plataforma para proponer cursos vacacionales y reunir el quórum mínimo de estudiantes
en el Politécnico Colombiano Jaime Isaza Cadavid.
 
> **Proyecto académico.** No es un canal oficial de la institución. La plataforma
> registra intención de matrícula; la inscripción oficial se realiza por Universitas XXI.
 
**Aplicación publicada:** [pendiente]
**Entrega:** 26 de septiembre de 2026
 
---
 
## Stack
 
Python 3.12 · Django 6.1 · PostgreSQL en Neon · HTMX · pytest · Render
 
---
 
## Puesta en marcha
 
No necesitas instalar PostgreSQL. La base de datos de desarrollo está en Neon.
 
### 1. Requisitos
 
- Python 3.12 o superior
- Git
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
En Windows, uv se instala desde PowerShell con:
 
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
 
Cierra y vuelve a abrir la terminal después de instalarlo.
 
### 2. Clonar e instalar dependencias
 
```bash
git clone https://github.com/svaltqt/Convoca.git
cd Convoca
uv sync
```
 
### 3. Crear tu archivo `.env`
 
En la raíz del proyecto, junto a `manage.py`, crea un archivo llamado `.env` con dos
líneas:
 
```
SECRET_KEY=tu-clave
DATABASE_URL=tu-cadena-de-conexion
```
 
**`SECRET_KEY`:** genera la tuya con
 
```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
 
**`DATABASE_URL`:** pídela por mensaje privado al responsable de infraestructura. Cada
integrante tiene su propia rama de base de datos:
 
| Rol | Rama de Neon |
|---|---|
| Infraestructura y maestras | `dev-infra` |
| Transaccional | `dev-transaccional` |
| Reportes y frontend | `dev-reportes` |
| QA y documentación | `dev-qa` |
 
Usa siempre tu rama, aunque estés ayudando en otra parte del proyecto.
 
> ⚠️ El `.env` contiene contraseñas. **Nunca lo subas al repositorio** (ya está en
> `.gitignore`) y nunca compartas tu cadena de conexión en el grupo.
 
### 4. Crear las tablas
 
```bash
uv run python manage.py migrate
```
 
La primera vez puede tardar unos segundos mientras la base de datos se activa.
 
### 5. Crear tu superusuario
 
```bash
uv run python manage.py createsuperuser
```
 
Te pide **correo institucional** y contraseña. No hay nombre de usuario: el inicio de
sesión es con el correo. Al escribir la contraseña no verás caracteres en pantalla, es
normal.
 
Cada integrante crea su propio superusuario en su rama.
 
### 6. Ejecutar
 
```bash
uv run python manage.py runserver
```
 
Abre <http://127.0.0.1:8000/admin> e inicia sesión con tu correo. Detén el servidor
con `Ctrl + C`.
 
---
 
## Flujo de trabajo con Git
 
**Nadie trabaja directo en `main`.** Todo cambio entra por una rama y un pull request.
 
```bash
git checkout main
git pull
git checkout -b feat/nombre-de-tu-tarea
```
 
Convención de nombres de rama:
 
| Prefijo | Uso | Ejemplo |
|---|---|---|
| `feat/` | Funcionalidad nueva | `feat/maestra-asignaturas` |
| `test/` | Pruebas | `test/adhesion-duplicada` |
| `fix/` | Corrección de errores | `fix/login-correo` |
| `docs/` | Documentación | `docs/manual-usuario` |
| `chore/` | Configuración | `chore/ci-github` |
 
Al terminar:
 
```bash
git add .
git commit -m "feat: descripción corta"
git push -u origin feat/nombre-de-tu-tarea
```
 
Abre el pull request con el enlace que muestra la terminal. Revisa los pull requests de
los demás en menos de doce horas.
 
### Si cambias un modelo
 
Todo cambio en un `models.py` va acompañado de su migración **en el mismo commit**:
 
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```
 
Sube el archivo que se crea en la carpeta `migrations/`. Sin él, los demás no pueden
actualizar su base de datos.
 
### Después de hacer `git pull`
 
Si alguien agregó dependencias o migraciones:
 
```bash
uv sync
uv run python manage.py migrate
```
 
### Si tu base de datos se daña
 
No la arregles a mano. Pide que borren tu rama de Neon y la recreen desde `production`,
actualiza tu `.env` si cambió la cadena, y corre `migrate` de nuevo.
 
---
 
## Pruebas
 
El proyecto se desarrolla con **TDD**: primero el test, verlo fallar, luego el código.
 
```bash
uv run pytest
```
 
Genera el informe en `docs/informe-pruebas.html` y la cobertura en
`htmlcov/index.html`. Si cambiaste un modelo y las pruebas fallan de forma extraña:
 
```bash
uv run pytest --create-db
```
 
---
 
## Uso de Claude Code
 
El archivo [`CLAUDE.md`](CLAUDE.md) contiene el modelo de datos, las reglas de negocio y
las convenciones del proyecto. Claude Code lo lee automáticamente si lo ejecutas desde
la raíz del repositorio.
 
Pídele **un criterio de aceptación a la vez**, y revisa y entiende todo el código que
genera antes de hacer commit. En la sustentación pueden preguntar por cualquier línea.
 
---
 
## Estructura
 
```
Convoca/
├── CLAUDE.md          Contexto y reglas para Claude Code
├── manage.py
├── config/
│   └── settings/      base, local (tu PC) y production (Render)
├── apps/
│   ├── usuarios/      Modelo de usuario y autenticación
│   ├── academico/     Facultades, programas, asignaturas, docentes
│   ├── periodos/      Periodos vacacionales
│   ├── propuestas/    Propuestas y adhesiones
│   └── reportes/      Reportes y exportación a PDF
├── templates/         Plantillas globales
├── static/            CSS, imágenes y logo
└── docs/              Historias de usuario, manuales e informe de pruebas
```
 
---
 
## Documentación
 
- [Historias de usuario](docs/)
- [Manual de usuario](docs/manual-usuario.md)
- [Manual de instalación y configuración](docs/manual-instalacion.md)
---
 
## Equipo
 
| Rol | Integrante |
|---|---|
| Infraestructura y maestras | |
| Transaccional | |
| Reportes y frontend | |
| QA y documentación | |
 


