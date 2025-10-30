from flask import Flask, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from config import Config
from db_connection import get_db_connection
from utils import obtener_todos_perfiles, obtener_perfil_por_slug

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración desde config.py
app.config.from_object(Config)

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