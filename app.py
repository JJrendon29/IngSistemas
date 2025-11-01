from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from config import Config
from db_connection import get_db_connection
from utils import obtener_todos_perfiles, obtener_perfil_por_slug
import os  # ← AGREGAR ESTA IMPORTACIÓN

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración desde config.py
app.config.from_object(Config)

# ========================================
# FUNCIÓN AUXILIAR PARA VERIFICAR ARCHIVOS
# ========================================

@app.context_processor
def utility_processor():
    """Función para verificar si existe un archivo en static"""
    def existe_archivo(ruta_relativa):
        ruta_completa = os.path.join(app.static_folder, ruta_relativa)
        return os.path.exists(ruta_completa)
    return dict(existe_archivo=existe_archivo)

# ========================================
# FUNCIONES PARA MANEJO DE ARCHIVOS
# ========================================

def guardar_archivos_perfil(perfil_slug, foto=None, cv=None):
    """
    Guarda los archivos de perfil con nombres estandarizados
    
    Args:
        perfil_slug: Slug del perfil (ej: 'juan-jose', 'carolina', 'valentina')
        foto: Archivo de imagen (FileStorage de Flask)
        cv: Archivo PDF del CV (FileStorage de Flask)
    
    Returns:
        dict: {'foto': bool, 'cv': bool} indicando qué se guardó
    """
    # Crear directorio del usuario
    usuario_dir = os.path.join(app.static_folder, 'usuarios', perfil_slug)
    os.makedirs(usuario_dir, exist_ok=True)
    
    resultado = {'foto': False, 'cv': False}
    
    # Guardar foto como perfil.jpg o perfil.png
    if foto and foto.filename:
        extension = foto.filename.rsplit('.', 1)[1].lower()
        if extension in ['png', 'jpg', 'jpeg']:
            foto_path = os.path.join(usuario_dir, f'perfil.{extension}')
            foto.save(foto_path)
            resultado['foto'] = True
    
    # Guardar CV como cv.pdf
    if cv and cv.filename:
        if cv.filename.lower().endswith('.pdf'):
            cv_path = os.path.join(usuario_dir, 'cv.pdf')
            cv.save(cv_path)
            resultado['cv'] = True
    
    return resultado

def tiene_cv(perfil_slug):
    """Verifica si existe el CV de un perfil"""
    cv_path = os.path.join(app.static_folder, 'usuarios', perfil_slug, 'cv.pdf')
    return os.path.exists(cv_path)

def obtener_ruta_imagen_perfil(perfil_slug):
    """
    Obtiene la ruta de la imagen de perfil (busca .jpg o .png)
    Retorna la ruta relativa o None si no existe
    """
    usuario_dir = os.path.join(app.static_folder, 'usuarios', perfil_slug)
    
    # Buscar perfil.jpg
    if os.path.exists(os.path.join(usuario_dir, 'perfil.jpg')):
        return f'usuarios/{perfil_slug}/perfil.jpg'
    
    # Buscar perfil.png
    if os.path.exists(os.path.join(usuario_dir, 'perfil.png')):
        return f'usuarios/{perfil_slug}/perfil.png'
    
    # Buscar perfil.jpeg
    if os.path.exists(os.path.join(usuario_dir, 'perfil.jpeg')):
        return f'usuarios/{perfil_slug}/perfil.jpeg'
    
    return None

def eliminar_archivos_perfil(perfil_slug):
    """Elimina todos los archivos de un perfil"""
    import shutil
    usuario_dir = os.path.join(app.static_folder, 'usuarios', perfil_slug)
    if os.path.exists(usuario_dir):
        shutil.rmtree(usuario_dir)
        return True
    return False

# ========================================
# RUTAS DE PERFILES
# ========================================

@app.route('/')
def index():
    """Página principal con grid/calendario de usuarios"""
    perfiles = obtener_todos_perfiles()
    return render_template('index.html', perfiles=perfiles)

@app.route('/perfil/<slug>')
def ver_perfil(slug):
    """Ver perfil individual de un usuario"""
    perfil = obtener_perfil_por_slug(slug)
    
    if perfil is None:
        abort(404)
    
    return render_template('perfil.html', perfil=perfil)

# ========================================
# RUTA PARA SUBIR ARCHIVOS DE PERFIL
# ========================================

@app.route('/perfil/<slug>/subir', methods=['POST'])
def subir_archivos_perfil(slug):
    """Subir o actualizar foto y CV de un perfil"""
    try:
        foto = request.files.get('foto')
        cv = request.files.get('cv')
        
        resultado = guardar_archivos_perfil(slug, foto, cv)
        
        if resultado['foto']:
            flash('Foto de perfil actualizada correctamente', 'success')
        if resultado['cv']:
            flash('CV actualizado correctamente', 'success')
        
        if not resultado['foto'] and not resultado['cv']:
            flash('No se subieron archivos', 'warning')
        
        return redirect(url_for('ver_perfil', slug=slug))
        
    except Exception as e:
        print(f"Error al subir archivos: {e}")
        flash('Error al subir los archivos', 'error')
        return redirect(url_for('ver_perfil', slug=slug))

# ========================================
# RUTA DE CONTACTO
# ========================================

@app.route('/contacto')
def contacto():
    """Página de contacto"""
    return render_template('contacto.html')

# ========================================
# RUTAS DE API - CONTACTOS
# ========================================

@app.route('/guardar_contacto', methods=['POST'])
def guardar_contacto():
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        empresa = request.form.get('empresa')
        correo = request.form.get('correo')
        celular = request.form.get('celular')
        mensaje = request.form.get('mensaje', '')
        
        # Validar que los campos requeridos no estén vacíos
        if not all([nombre, empresa, correo, celular]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return redirect(url_for('contacto'))
        
        # Conectar a la base de datos
        connection = get_db_connection()
        if connection is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('contacto'))
        
        # Insertar el contacto en la base de datos
        with connection.cursor() as cursor:
            sql = """INSERT INTO contactos (nombre, empresa, correo, celular, mensaje, fecha_registro) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, empresa, correo, celular, mensaje, datetime.now()))
            connection.commit()
        
        connection.close()
        flash('¡Contacto guardado exitosamente!', 'success')
        return redirect(url_for('contacto'))
        
    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        flash('Error al guardar el contacto', 'error')
        return redirect(url_for('contacto'))

@app.route('/api/contactos', methods=['GET'])
def obtener_contactos():
    """API para obtener todos los contactos"""
    try:
        connection = get_db_connection()
        if connection is None:
            return {"error": "Error de conexión"}, 500
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM contactos ORDER BY fecha_registro DESC")
            contactos = cursor.fetchall()
        
        connection.close()
        return {"contactos": contactos}, 200
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}, 500

@app.route('/api/contactos/<int:id>', methods=['PUT'])
def actualizar_contacto(id):
    """API para actualizar un contacto"""
    try:
        data = request.get_json()
        connection = get_db_connection()
        
        if connection is None:
            return {"error": "Error de conexión"}, 500
        
        with connection.cursor() as cursor:
            sql = """UPDATE contactos 
                     SET nombre=%s, empresa=%s, correo=%s, celular=%s, mensaje=%s 
                     WHERE id=%s"""
            cursor.execute(sql, (
                data['nombre'], 
                data['empresa'], 
                data['correo'], 
                data['celular'], 
                data['mensaje'], 
                id
            ))
            connection.commit()
        
        connection.close()
        return {"mensaje": "Contacto actualizado"}, 200
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/contactos/<int:id>', methods=['DELETE'])
def eliminar_contacto(id):
    """API para eliminar un contacto"""
    try:
        connection = get_db_connection()
        
        if connection is None:
            return {"error": "Error de conexión"}, 500
        
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM contactos WHERE id=%s", (id,))
            connection.commit()
        
        connection.close()
        return {"mensaje": "Contacto eliminado"}, 200
        
    except Exception as e:
        return {"error": str(e)}, 500

# ========================================
# MANEJADORES DE ERRORES
# ========================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return "Error interno del servidor", 500

# ========================================
# EJECUTAR APLICACIÓN
# ========================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)