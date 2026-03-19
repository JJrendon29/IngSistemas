# Sistema de Perfiles de Practicantes
## Universidad Católica Luis Amigó

Sistema web para gestionar perfiles de practicantes de Ingeniería de Sistemas. Permite a estudiantes crear su perfil y a administradores aprobarlos para publicación.

---

## Características

- **Registro con correo institucional**: Solo `@amigo.edu.co`
- **Roles**: Estudiante y Administrador
- **Flujo de aprobación**: Estudiante crea/edita perfil → queda pendiente → Admin aprueba o rechaza
- **Habilidades como filtro**: Las empresas pueden buscar perfiles por habilidades
- **Subida de archivos**: Foto de perfil (JPG/PNG) y CV (PDF)
- **Panel de administración**: Gestión de perfiles y contactos
- **Modo oscuro**
- **Responsive**

---

## Requisitos

- Python 3.8+
- MySQL 5.7+
- pip

---

## Instalación

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

### 4. Configurar base de datos

Ejecutar el archivo `schema.sql` en MySQL:

```bash
mysql -u root -p < schema.sql
```

Esto crea:
- Base de datos `practicantes_db`
- Todas las tablas necesarias
- Usuario admin por defecto

### 5. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus datos de MySQL:

```
SECRET_KEY=tu-clave-secreta-aqui
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=tu-password
MYSQL_DB=practicantes_db
MYSQL_PORT=3306
DOMINIO_INSTITUCIONAL=amigo.edu.co
```

### 6. Ejecutar

```bash
python app.py
```

Abrir http://localhost:5000

---

## Credenciales por defecto

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@amigo.edu.co | admin123 |

**⚠️ Cambiar la contraseña del admin en producción.**

---

## Estructura del proyecto

```
proyecto/
├── app.py                  # Aplicación principal (rutas)
├── config.py               # Configuración
├── db_connection.py        # Conexión a MySQL
├── models.py               # Modelos y queries a BD
├── schema.sql              # Script SQL para crear tablas
├── requirements.txt        # Dependencias Python
├── .env.example            # Plantilla de variables de entorno
├── .gitignore
├── static/
│   ├── css/style.css       # Estilos (colores institucionales)
│   ├── js/script.js        # JavaScript
│   └── usuarios/           # Fotos y CVs (por carpeta de slug)
│       └── juan-perez/
│           ├── perfil.jpg
│           └── cv.pdf
└── templates/
    ├── base.html            # Template base
    ├── index.html           # Página principal (grid de perfiles)
    ├── perfil.html          # Perfil público individual
    ├── contacto.html        # Formulario de contacto
    ├── login.html           # Inicio de sesión
    ├── registro.html        # Registro de cuenta
    ├── mi_perfil.html       # Panel del estudiante
    ├── editar_perfil.html   # Crear/editar perfil
    ├── 403.html             # Error acceso denegado
    ├── 404.html             # Error página no encontrada
    └── admin/
        ├── panel.html       # Panel admin (gestión perfiles)
        └── contactos.html   # Gestión de contactos
```

---

## Flujo de uso

### Estudiante
1. Se registra con correo `@amigo.edu.co`
2. Inicia sesión → va a "Mi Perfil"
3. Crea su perfil (nombre, título, descripción, habilidades, foto, CV)
4. El perfil queda en estado **pendiente**
5. Cuando el admin lo aprueba, aparece en la página principal

### Administrador
1. Inicia sesión con cuenta admin
2. Va a "Admin" → ve perfiles pendientes
3. Puede **aprobar**, **rechazar** o **eliminar** perfiles
4. También gestiona los contactos recibidos

### Empresa/Visitante
1. Ve la página principal con perfiles aprobados
2. Puede filtrar por habilidad
3. Entra al perfil de un practicante
4. Descarga su CV o lo contacta
5. Puede dejar sus datos en el formulario de contacto

---

## Notas técnicas

- Las contraseñas se hashean con **bcrypt**
- Las sesiones se manejan con **Flask-Login**
- Al editar un perfil, vuelve a estado pendiente automáticamente
- Los archivos se guardan en `static/usuarios/<slug>/`
- Las habilidades son texto libre (no catálogo fijo) para flexibilidad
