from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from config import Config
from db_connection import get_db_connection

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración desde config.py
app.config.from_object(Config)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de perfiles
@app.route('/perfiles')
def perfiles():
    return render_template('perfiles.html')

# Ruta para procesar el formulario de contacto
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
            return redirect(url_for('perfiles'))
        
        # Conectar a la base de datos usando db_connection.py
        connection = get_db_connection()
        if connection is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('perfiles'))
        
        # Insertar el contacto en la base de datos
        with connection.cursor() as cursor:
            sql = """INSERT INTO contactos (nombre, empresa, correo, celular, mensaje, fecha_registro) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, empresa, correo, celular, mensaje, datetime.now()))
            connection.commit()
        
        connection.close()
        flash('¡Contacto guardado exitosamente!', 'success')
        return redirect(url_for('perfiles'))
        
    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        flash('Error al guardar el contacto', 'error')
        return redirect(url_for('perfiles'))
    
# Ruta para obtener todos los contactos (API JSON)
@app.route('/api/contactos', methods=['GET'])
def obtener_contactos():
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

# Ruta para actualizar un contacto
@app.route('/api/contactos/<int:id>', methods=['PUT'])
def actualizar_contacto(id):
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

# Ruta para eliminar un contacto
@app.route('/api/contactos/<int:id>', methods=['DELETE'])
def eliminar_contacto(id):
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

# Manejador de errores 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Manejador de errores 500
@app.errorhandler(500)
def internal_error(e):
    return "Error interno del servidor", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)