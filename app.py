from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from functools import wraps
import os
import re
import shutil

from config import Config
from db_connection import get_db_connection
from models import (
    Usuario, obtener_todos_perfiles, obtener_perfil_por_slug,
    obtener_perfil_por_usuario, crear_perfil, actualizar_perfil,
    guardar_habilidades, guardar_formacion, guardar_idiomas,
    buscar_perfiles_por_habilidad, obtener_habilidades_unicas
)

# ========================================
# CREAR APP
# ========================================

app = Flask(__name__)
app.config.from_object(Config)

# ========================================
# FLASK-LOGIN
# ========================================

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.obtener_por_id(int(user_id))


# ========================================
# DECORADOR: SOLO ADMIN
# ========================================

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.es_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ========================================
# CONTEXT PROCESSOR
# ========================================

@app.context_processor
def utility_processor():
    def existe_archivo(ruta_relativa):
        ruta_completa = os.path.join(app.static_folder, ruta_relativa)
        return os.path.exists(ruta_completa)
    return dict(existe_archivo=existe_archivo)


# ========================================
# HELPERS DE ARCHIVOS
# ========================================

def generar_slug(nombre):
    """Genera un slug limpio a partir de un nombre"""
    slug = nombre.lower().strip()
    slug = re.sub(r'[áàäâ]', 'a', slug)
    slug = re.sub(r'[éèëê]', 'e', slug)
    slug = re.sub(r'[íìïî]', 'i', slug)
    slug = re.sub(r'[óòöô]', 'o', slug)
    slug = re.sub(r'[úùüû]', 'u', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

def validar_urls_perfil(github, linkedin):
    """Valida que las URLs sean de GitHub y LinkedIn respectivamente"""
    errores = []
    
    if github:
        if not re.match(r'^https?://(www\.)?github\.com/[a-zA-Z0-9_-]+/?$', github):
            errores.append('El link de GitHub debe ser como: https://github.com/tu-usuario')
    
    if linkedin:
        if not re.match(r'^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?$', linkedin):
            errores.append('El link de LinkedIn debe ser como: https://linkedin.com/in/tu-perfil')
    
    return errores


def guardar_archivo_perfil(perfil_slug, archivo, tipo):
    """
    Guarda foto o CV en static/usuarios/<slug>/
    tipo: 'foto' o 'cv'
    Retorna la ruta relativa guardada o None
    """
    if not archivo or not archivo.filename:
        return None

    usuario_dir = os.path.join(app.static_folder, 'usuarios', perfil_slug)
    os.makedirs(usuario_dir, exist_ok=True)

    if tipo == 'foto':
        ext = archivo.filename.rsplit('.', 1)[-1].lower()
        if ext not in ('jpg', 'jpeg', 'png'):
            return None
        filename = f'perfil.{ext}'
        # Eliminar fotos anteriores
        for old in ('perfil.jpg', 'perfil.jpeg', 'perfil.png'):
            old_path = os.path.join(usuario_dir, old)
            if os.path.exists(old_path):
                os.remove(old_path)
    elif tipo == 'cv':
        if not archivo.filename.lower().endswith('.pdf'):
            return None
        filename = 'cv.pdf'
    else:
        return None

    filepath = os.path.join(usuario_dir, filename)
    archivo.save(filepath)
    return f'usuarios/{perfil_slug}/{filename}'


def obtener_ruta_imagen_perfil(perfil_slug):
    """Busca la imagen de perfil en disco"""
    usuario_dir = os.path.join(app.static_folder, 'usuarios', perfil_slug)
    for ext in ('jpg', 'jpeg', 'png'):
        if os.path.exists(os.path.join(usuario_dir, f'perfil.{ext}')):
            return f'usuarios/{perfil_slug}/perfil.{ext}'
    return None


# ========================================
# RUTAS: AUTENTICACIÓN
# ========================================

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validar dominio institucional
        dominio = app.config.get('DOMINIO_INSTITUCIONAL', 'amigo.edu.co')
        if not email.endswith(f'@{dominio}'):
            flash(f'Solo se permiten correos @{dominio}', 'error')
            return render_template('registro.html')

        # Validar contraseña segura
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'error')
            return render_template('registro.html')

        if not re.search(r'[A-Z]', password):
            flash('La contraseña debe tener al menos una letra mayúscula', 'error')
            return render_template('registro.html')

        if not re.search(r'[a-z]', password):
            flash('La contraseña debe tener al menos una letra minúscula', 'error')
            return render_template('registro.html')

        if not re.search(r'[0-9]', password):
            flash('La contraseña debe tener al menos un número', 'error')
            return render_template('registro.html')

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('La contraseña debe tener al menos un carácter especial (!@#$%^&*...)', 'error')
            return render_template('registro.html')

        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('registro.html')

        # Verificar que no exista
        if Usuario.obtener_por_email(email):
            flash('Ya existe una cuenta con ese correo', 'error')
            return render_template('registro.html')

        user_id = Usuario.crear(email, password, rol='estudiante')
        if user_id:
            flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al crear la cuenta', 'error')

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        usuario = Usuario.obtener_por_email(email)

        if usuario and usuario.activo and usuario.verificar_password(password):
            login_user(usuario)
            next_page = request.args.get('next')
            flash('Sesión iniciada correctamente', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('index'))


# ========================================
# RUTAS: PÁGINAS PÚBLICAS
# ========================================

@app.route('/')
def index():
    busqueda = request.args.get('habilidad', '').strip()
    if busqueda:
        perfiles = buscar_perfiles_por_habilidad(busqueda)
    else:
        perfiles = obtener_todos_perfiles(solo_aprobados=True)

    habilidades_disponibles = obtener_habilidades_unicas()
    return render_template('index.html',
                           perfiles=perfiles,
                           habilidades_disponibles=habilidades_disponibles,
                           busqueda=busqueda)


@app.route('/perfil/<slug>')
def ver_perfil(slug):
    perfil = obtener_perfil_por_slug(slug, solo_aprobados=True)
    if perfil is None:
        abort(404)
    # Verificar imagen en disco
    perfil['_imagen_disco'] = obtener_ruta_imagen_perfil(slug)
    return render_template('perfil.html', perfil=perfil)


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


@app.route('/guardar_contacto', methods=['POST'])
def guardar_contacto():
    try:
        nombre = request.form.get('nombre')
        empresa = request.form.get('empresa')
        correo = request.form.get('correo')
        celular = request.form.get('celular')
        mensaje = request.form.get('mensaje', '')

        if not all([nombre, empresa, correo, celular]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return redirect(url_for('contacto'))

        conn = get_db_connection()
        if conn is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('contacto'))

        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO contactos (nombre, empresa, correo, celular, mensaje, fecha_registro) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (nombre, empresa, correo, celular, mensaje, datetime.now())
            )
            conn.commit()
        conn.close()

        flash('¡Mensaje enviado exitosamente!', 'success')
        return redirect(url_for('contacto'))

    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        flash('Error al guardar el contacto', 'error')
        return redirect(url_for('contacto'))


# ========================================
# RUTAS: PANEL DEL ESTUDIANTE
# ========================================

@app.route('/mi-perfil')
@login_required
def mi_perfil():
    perfil = obtener_perfil_por_usuario(current_user.id)
    return render_template('mi_perfil.html', perfil=perfil)


@app.route('/mi-perfil/crear', methods=['GET', 'POST'])
@login_required
def crear_mi_perfil():
    # Verificar que no tenga perfil ya
    perfil_existente = obtener_perfil_por_usuario(current_user.id)
    if perfil_existente:
        return redirect(url_for('editar_mi_perfil'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template('editar_perfil.html', perfil=None, modo='crear')

        slug = generar_slug(nombre)

        github = request.form.get('github', '').strip()
        linkedin = request.form.get('linkedin', '').strip()

        errores_url = validar_urls_perfil(github, linkedin)
        if errores_url:
            for error in errores_url:
                flash(error, 'error')
            return render_template('editar_perfil.html', perfil=None, modo='crear')

        perfil_id = crear_perfil(
            usuario_id=current_user.id,
            nombre=nombre,
            slug=slug,
            titulo=request.form.get('titulo', '').strip(),
            descripcion=request.form.get('descripcion', '').strip(),
            email_contacto=request.form.get('email_contacto', '').strip(),
            github=request.form.get('github', '').strip(),
            linkedin=request.form.get('linkedin', '').strip()
        )

        if perfil_id:
            # Guardar archivos
            foto = request.files.get('foto')
            cv = request.files.get('cv')
            if foto and foto.filename:
                ruta = guardar_archivo_perfil(slug, foto, 'foto')
                if ruta:
                    actualizar_perfil(perfil_id, foto_url=ruta, estado='pendiente')
            if cv and cv.filename:
                ruta = guardar_archivo_perfil(slug, cv, 'cv')
                if ruta:
                    actualizar_perfil(perfil_id, cv_url=ruta, estado='pendiente')

            # Guardar habilidades
            _guardar_habilidades_desde_form(perfil_id, request.form)
            _guardar_formacion_desde_form(perfil_id, request.form)
            _guardar_idiomas_desde_form(perfil_id, request.form)

            flash('Perfil creado. Está pendiente de aprobación por el administrador.', 'success')
            return redirect(url_for('mi_perfil'))
        else:
            flash('Error al crear el perfil', 'error')

    return render_template('editar_perfil.html', perfil=None, modo='crear')


@app.route('/mi-perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_mi_perfil():
    perfil = obtener_perfil_por_usuario(current_user.id)
    if not perfil:
        return redirect(url_for('crear_mi_perfil'))

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template('editar_perfil.html', perfil=perfil, modo='editar')

        nuevo_slug = generar_slug(nombre)

        # Si cambió el slug, renombrar carpeta de archivos
        if nuevo_slug != perfil['slug']:
            old_dir = os.path.join(app.static_folder, 'usuarios', perfil['slug'])
            new_dir = os.path.join(app.static_folder, 'usuarios', nuevo_slug)
            if os.path.exists(old_dir):
                shutil.move(old_dir, new_dir)

        github = request.form.get('github', '').strip()
        linkedin = request.form.get('linkedin', '').strip()

        errores_url = validar_urls_perfil(github, linkedin)
        if errores_url:
            for error in errores_url:
                flash(error, 'error')
            return render_template('editar_perfil.html', perfil=perfil, modo='editar')

        actualizar_perfil(
            perfil['id'],
            nombre=nombre,
            slug=nuevo_slug,
            titulo=request.form.get('titulo', '').strip(),
            descripcion=request.form.get('descripcion', '').strip(),
            email_contacto=request.form.get('email_contacto', '').strip(),
            github=request.form.get('github', '').strip(),
            linkedin=request.form.get('linkedin', '').strip()
        )

        # Archivos
        foto = request.files.get('foto')
        cv = request.files.get('cv')
        if foto and foto.filename:
            ruta = guardar_archivo_perfil(nuevo_slug, foto, 'foto')
            if ruta:
                actualizar_perfil(perfil['id'], foto_url=ruta, estado='pendiente')
        if cv and cv.filename:
            ruta = guardar_archivo_perfil(nuevo_slug, cv, 'cv')
            if ruta:
                actualizar_perfil(perfil['id'], cv_url=ruta, estado='pendiente')

        # Habilidades, formación, idiomas
        _guardar_habilidades_desde_form(perfil['id'], request.form)
        _guardar_formacion_desde_form(perfil['id'], request.form)
        _guardar_idiomas_desde_form(perfil['id'], request.form)

        flash('Perfil actualizado. Está pendiente de aprobación.', 'success')
        return redirect(url_for('mi_perfil'))

    return render_template('editar_perfil.html', perfil=perfil, modo='editar')


# ========================================
# RUTAS: PANEL DE ADMINISTRACIÓN
# ========================================

@app.route('/admin')
@admin_required
def admin_panel():
    perfiles = obtener_todos_perfiles(solo_aprobados=False)
    return render_template('admin/panel.html', perfiles=perfiles)


@app.route('/admin/perfil/<int:perfil_id>/aprobar', methods=['POST'])
@admin_required
def aprobar_perfil(perfil_id):
    actualizar_perfil(perfil_id, estado='aprobado')
    flash('Perfil aprobado', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/perfil/<int:perfil_id>/rechazar', methods=['POST'])
@admin_required
def rechazar_perfil(perfil_id):
    actualizar_perfil(perfil_id, estado='rechazado')
    flash('Perfil rechazado', 'warning')
    return redirect(url_for('admin_panel'))


@app.route('/admin/perfil/<int:perfil_id>/eliminar', methods=['POST'])
@admin_required
def eliminar_perfil_admin(perfil_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                # Obtener slug para eliminar archivos
                cursor.execute("SELECT slug FROM perfiles WHERE id = %s", (perfil_id,))
                perfil = cursor.fetchone()
                if perfil:
                    usuario_dir = os.path.join(
                        app.static_folder, 'usuarios', perfil['slug']
                    )
                    if os.path.exists(usuario_dir):
                        shutil.rmtree(usuario_dir)
                    cursor.execute("DELETE FROM perfiles WHERE id = %s", (perfil_id,))
                    conn.commit()
                    flash('Perfil eliminado', 'success')
        except Exception as e:
            print(f"Error al eliminar perfil: {e}")
            conn.rollback()
            flash('Error al eliminar el perfil', 'error')
        finally:
            conn.close()

    return redirect(url_for('admin_panel'))


@app.route('/admin/contactos')
@admin_required
def admin_contactos():
    conn = get_db_connection()
    contactos = []
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM contactos ORDER BY fecha_registro DESC"
                )
                contactos = cursor.fetchall()
        finally:
            conn.close()

    return render_template('admin/contactos.html', contactos=contactos)


@app.route('/admin/contactos/<int:id>/eliminar', methods=['POST'])
@admin_required
def eliminar_contacto(id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM contactos WHERE id = %s", (id,))
                conn.commit()
            flash('Contacto eliminado', 'success')
        finally:
            conn.close()
    return redirect(url_for('admin_contactos'))


# ========================================
# HELPERS: PARSEAR FORMULARIOS DINÁMICOS
# ========================================

def _guardar_habilidades_desde_form(perfil_id, form):
    """Parsea habilidades del formulario dinámico"""
    habilidades = []
    i = 0
    while True:
        nombre = form.get(f'hab_nombre_{i}', '').strip()
        if nombre == '' and i > 0:
            # Verificar si hay más
            next_nombre = form.get(f'hab_nombre_{i+1}', '').strip()
            if not next_nombre:
                break
            i += 1
            continue
        if nombre:
            nivel = form.get(f'hab_nivel_{i}', 'intermedio')
            habilidades.append({'nombre': nombre, 'nivel': nivel})
        i += 1
        if i > 50:  # Safety limit
            break
    guardar_habilidades(perfil_id, habilidades)


def _guardar_formacion_desde_form(perfil_id, form):
    """Parsea formación del formulario dinámico"""
    formaciones = []
    i = 0
    while True:
        titulo = form.get(f'form_titulo_{i}', '').strip()
        if titulo == '' and i > 0:
            next_titulo = form.get(f'form_titulo_{i+1}', '').strip()
            if not next_titulo:
                break
            i += 1
            continue
        if titulo:
            formaciones.append({
                'titulo': titulo,
                'institucion': form.get(f'form_institucion_{i}', '').strip(),
                'anio': form.get(f'form_anio_{i}', '').strip()
            })
        i += 1
        if i > 20:
            break
    guardar_formacion(perfil_id, formaciones)


def _guardar_idiomas_desde_form(perfil_id, form):
    """Parsea idiomas del formulario dinámico"""
    idiomas_list = []
    i = 0
    while True:
        idioma = form.get(f'idioma_nombre_{i}', '').strip()
        if idioma == '' and i > 0:
            next_idioma = form.get(f'idioma_nombre_{i+1}', '').strip()
            if not next_idioma:
                break
            i += 1
            continue
        if idioma:
            idiomas_list.append({
                'idioma': idioma,
                'nivel': form.get(f'idioma_nivel_{i}', '').strip()
            })
        i += 1
        if i > 20:
            break
    guardar_idiomas(perfil_id, idiomas_list)


# ========================================
# ERRORES
# ========================================

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return "Error interno del servidor", 500


# ========================================
# EJECUTAR
# ========================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)
