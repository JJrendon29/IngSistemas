# Sistema de Perfiles de Practicantes
## Universidad Católica Luis Amigó

Sistema web para gestionar y publicar perfiles de practicantes del programa de Ingeniería de Sistemas. Los estudiantes crean su perfil, el administrador lo revisa campo por campo, y las empresas pueden buscar y contactar practicantes.

---

## Características

- **Registro con correo institucional**: Solo se aceptan correos `@amigo.edu.co`
- **Roles**: Estudiante y Administrador
- **Flujo de aprobación campo por campo**: El admin revisa cada sección del perfil individualmente (`revisiones_campo`) con comentarios por campo
- **Verificación GitHub via OAuth**: El estudiante conecta su cuenta de GitHub para verificar su perfil
- **Verificación de LinkedIn**: El sistema valida que la URL de LinkedIn sea accesible
- **Catálogos dinámicos**: Títulos, habilidades por categoría (lenguaje, framework, base de datos, herramienta), idiomas y programas académicos gestionados desde el panel admin
- **Formación Actual**: Programa académico UCatólica (Ingeniería de Sistemas o Tecnología en Desarrollo de Software) y semestre actual
- **Formación Previa**: Historial académico con autocompletado de instituciones educativas via API de datos.gov.co
- **Formulario de edición por etapas**: Wizard de 4 pasos (Básico + Foto/CV → Contacto y Redes → Habilidades → Formación e Idiomas)
- **Subida de archivos**: Foto de perfil (JPG/PNG) y CV (PDF) almacenados en `static/usuarios/<perfil_id>/`
- **Búsqueda con filtros combinables**: Por título profesional, habilidad e idioma, con paginación
- **Formulario de contacto**: Las empresas envían sus datos e indican qué practicantes les interesan
- **Panel admin completo**:
  - Gestión de perfiles con revisión campo por campo
  - Gestión de contactos con filtros, exportación a CSV y notas internas
  - Gestión de usuarios (reset de contraseña)
  - Datos maestros: catálogo de habilidades (agregar, editar, activar/desactivar)
- **Lucide Icons**, **modo oscuro** y diseño **responsive**
- **Deployment listo para Railway**: `Procfile`, `gunicorn`, `runtime.txt`

---

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip

---

## Instalación (desarrollo local)

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd proyecto
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus datos (ver sección [Variables de entorno](#variables-de-entorno)).

### 5. Inicializar la base de datos

```bash
mysql -u root -p < schema.sql
mysql -u root -p practicantes_db < catalogos.sql
```

`schema.sql` crea las tablas y el usuario admin por defecto.
`catalogos.sql` puebla los catálogos de habilidades, idiomas y títulos.

### 6. Ejecutar

```bash
python app.py
```

Abrir http://localhost:5000

---

## Variables de entorno

Copiar `.env.example` a `.env` y completar cada valor:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask para firmar sesiones. Usar un valor largo y aleatorio en producción. |
| `MYSQL_HOST` | Host de la base de datos MySQL (ej. `localhost`). |
| `MYSQL_USER` | Usuario de MySQL (ej. `root`). |
| `MYSQL_PASSWORD` | Contraseña del usuario MySQL. |
| `MYSQL_DB` | Nombre de la base de datos (usar `practicantes_db`). |
| `MYSQL_PORT` | Puerto de MySQL (por defecto `3306`). |
| `DOMINIO_INSTITUCIONAL` | Dominio permitido para registro (por defecto `amigo.edu.co`). |
| `GITHUB_CLIENT_ID` | Client ID de la OAuth App de GitHub (para verificación de perfiles). |
| `GITHUB_CLIENT_SECRET` | Client Secret de la OAuth App de GitHub. |
| `DEBUG` | Modo debug de Flask (`True` en desarrollo, `False` en producción). |

---

## Estructura del proyecto

```
proyecto/
├── app.py                      # Entrada de la aplicación, registro de blueprints
├── config.py                   # Carga de variables de entorno y configuración
├── db_connection.py            # Función get_db_connection() con PyMySQL
├── utils.py                    # Helpers: generar_slug, guardar_archivo, admin_required
├── Procfile                    # Comando de inicio para Railway/Heroku (gunicorn)
├── runtime.txt                 # Versión de Python para Railway
├── requirements.txt            # Dependencias Python
├── schema.sql                  # Script SQL para crear la BD desde cero
├── catalogos.sql               # Script SQL para poblar catálogos
├── .env.example                # Plantilla de variables de entorno
├── models/
│   ├── __init__.py             # Re-exporta todas las funciones de modelos
│   ├── usuario.py              # Clase Usuario (Flask-Login) y autenticación
│   ├── perfil.py               # CRUD de perfiles, habilidades, formación, idiomas
│   ├── catalogo.py             # Lectura y gestión de catálogos dinámicos
│   ├── busqueda.py             # Búsqueda de perfiles con filtros combinables
│   └── revision.py             # Sistema de revisión campo por campo
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Blueprint: registro, login, logout, GitHub OAuth
│   ├── public.py               # Blueprint: index, perfil público, contacto, API instituciones
│   ├── perfil.py               # Blueprint: mi-perfil, crear/editar perfil (estudiante)
│   └── admin.py                # Blueprint: panel admin, perfiles, contactos, usuarios, datos maestros
├── static/
│   ├── css/
│   │   ├── style.css           # Estilos globales y colores institucionales
│   │   ├── admin.css           # Estilos del panel de administración
│   │   └── perfil.css          # Estilos de la página de perfil público
│   ├── js/
│   │   ├── script.js           # Dark mode, navegación, interacciones generales
│   │   └── editar_perfil.js    # Wizard de 4 pasos, filas dinámicas de formación/idiomas
│   └── usuarios/               # Archivos subidos, organizados por perfil_id
│       └── <perfil_id>/
│           ├── perfil.jpg
│           └── cv.pdf
└── templates/
    ├── base.html               # Template base con nav, footer y modo oscuro
    ├── index.html              # Página principal: grid de perfiles, filtros, paginación
    ├── perfil.html             # Perfil público individual
    ├── contacto.html           # Formulario de contacto para empresas
    ├── login.html              # Inicio de sesión
    ├── registro.html           # Registro de cuenta institucional
    ├── mi_perfil.html          # Dashboard del estudiante (estado, revisiones)
    ├── editar_perfil.html      # Crear/editar perfil (wizard 4 pasos)
    ├── 403.html                # Error: acceso denegado
    ├── 404.html                # Error: página no encontrada
    └── admin/
        ├── panel.html          # Dashboard admin: lista de perfiles y estados
        ├── revisar_perfil.html # Revisión campo por campo con comentarios
        ├── contactos.html      # Gestión de contactos (filtros, CSV, notas)
        ├── usuarios.html       # Lista de usuarios y reset de contraseña
        └── datos_maestros.html # Gestión del catálogo de habilidades
```

---

## Flujo de uso

### Estudiante
1. Se registra con correo `@amigo.edu.co` y contraseña segura
2. Inicia sesión → va a "Mi Perfil"
3. Completa el wizard de 4 pasos: información básica, habilidades del catálogo, formación académica (con autocompletado de instituciones), y subida de foto/CV
4. Opcionalmente conecta su GitHub via OAuth y agrega su URL de LinkedIn
5. El perfil queda en estado **pendiente** hasta que el admin lo revise
6. Si el admin deja comentarios por campo, el estudiante los ve en su dashboard, corrige y reenvía

### Administrador
1. Inicia sesión con cuenta admin
2. Panel → ve todos los perfiles con sus estados
3. Entra a "Revisar" → aprueba o rechaza cada campo individualmente con comentarios
4. El perfil pasa a **aprobado** (visible en la página principal), **rechazado** o **en revisión**
5. Gestiona contactos recibidos: cambia su estado (nuevo → contactado → en proceso → cerrado), agrega notas, exporta a CSV
6. Desde "Datos Maestros" gestiona el catálogo de habilidades
7. Desde "Usuarios" puede resetear contraseñas

### Empresa / Visitante
1. Navega la página principal con perfiles aprobados
2. Filtra por título profesional, habilidad específica o idioma
3. Entra al perfil de un practicante, ve su información, descarga su CV
4. Completa el formulario de contacto indicando qué practicantes le interesan
5. El administrador recibe el contacto y hace seguimiento desde el panel

---

## Credenciales por defecto

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@amigo.edu.co | admin123 |

> **Cambiar la contraseña del admin antes de usar en producción.**

---

## Deployment en Railway

1. Crear un nuevo proyecto en [Railway](https://railway.app)
2. Agregar un servicio **MySQL** al proyecto y copiar las credenciales de conexión
3. Conectar el repositorio de GitHub al servicio web
4. Configurar las variables de entorno en Railway con los valores del `.env.example` (usar las credenciales del MySQL de Railway para `MYSQL_HOST`, `MYSQL_USER`, etc.)
5. Inicializar la base de datos ejecutando `schema.sql` y `catalogos.sql` contra el MySQL de Railway:
   ```bash
   mysql -h <MYSQL_HOST> -u <MYSQL_USER> -p<MYSQL_PASSWORD> --port <MYSQL_PORT> < schema.sql
   mysql -h <MYSQL_HOST> -u <MYSQL_USER> -p<MYSQL_PASSWORD> --port <MYSQL_PORT> practicantes_db < catalogos.sql
   ```
6. Railway detecta el `Procfile` y despliega con `gunicorn app:app`
7. Generar un dominio público desde la configuración del servicio web en Railway
8. Actualizar la **URL de callback de la OAuth App de GitHub** al nuevo dominio:
   `https://<tu-dominio>.railway.app/auth/github/callback`

---

## Configuración para Producción

Esta sección aplica cuando la universidad quiera poner el sistema en producción real:

- **Cambiar la contraseña del admin por defecto** inmediatamente después del primer despliegue
- **Generar un SECRET_KEY seguro**:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Configurar `DEBUG=False`** en las variables de entorno
- **Actualizar la URL de callback de GitHub OAuth** en la configuración de la OAuth App en GitHub al dominio de producción definitivo
- **Almacenamiento de archivos**: Actualmente las fotos y CVs se guardan en el filesystem del servidor (`static/usuarios/`). Si se espera alto volumen de usuarios, considerar un servicio externo (AWS S3, Google Cloud Storage) para mayor durabilidad y escalabilidad
- **Verificación de correo electrónico**: Implementar envío de email con token de confirmación para validar que los correos `@amigo.edu.co` registrados sean reales
- **HTTPS**: Railway lo provee por defecto. Si se usa otro hosting, verificar que esté configurado
- **Backups de la base de datos**: Configurar backups automáticos del MySQL en producción
- **Actualizar catálogos**: Revisar y actualizar el catálogo de habilidades desde el panel de Datos Maestros según las necesidades del programa académico

---

## Notas técnicas

- **Contraseñas** hasheadas con `bcrypt`
- **Sesiones** manejadas con `Flask-Login`
- **Arquitectura modular**: Flask Blueprints (`auth`, `public`, `perfil`, `admin`) con modelos separados en `models/`
- **Archivos subidos** almacenados en `static/usuarios/<perfil_id>/` (organizado por ID de perfil, no por slug)
- **Revisión campo por campo** implementada con `INSERT INTO revisiones_campo ... ON DUPLICATE KEY UPDATE`, permite al admin dar feedback específico por sección
- **API de Datos Abiertos Colombia** (`datos.gov.co`) para autocompletado de instituciones educativas en el formulario de formación previa
- Al editar un perfil, el estado vuelve a **pendiente** automáticamente y se resetean las revisiones de campos rechazados
