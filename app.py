from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_cambiar'

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tu_password_mysql',
    'database': 'proyecto_unidades',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = pymysql.connect(**db_config)
        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Rutas de las unidades
@app.route('/unidad1')
def unidad1():
    return render_template('unidad1.html')

@app.route('/unidad2')
def unidad2():
    return render_template('unidad2.html')

@app.route('/unidad3')
def unidad3():
    return render_template('unidad3.html')

@app.route('/unidad4')
def unidad4():
    return render_template('unidad4.html')

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
        
        # Conectar a la base de datos
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


# Manejador de errores 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)