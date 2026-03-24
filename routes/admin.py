import csv
import io
import os
import shutil
from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response, current_app
from flask_login import current_user

from db_connection import get_db_connection
from models import (
    Usuario,
    obtener_todos_perfiles,
    actualizar_perfil,
    obtener_revisiones_perfil,
    guardar_revisiones,
    obtener_todos_usuarios,
    resetear_password,
    CAMPOS_REVISABLES,
    _obtener_habilidades,
    _obtener_formacion,
    _obtener_idiomas,
)
from utils import admin_required, obtener_ruta_imagen_perfil

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ========================================
# RUTAS: PANEL DE ADMINISTRACIÓN
# ========================================

@admin_bp.route('')
@admin_required
def admin_panel():
    perfiles = obtener_todos_perfiles(solo_aprobados=False)
    return render_template('admin/panel.html', perfiles=perfiles)


@admin_bp.route('/perfil/<int:perfil_id>/aprobar', methods=['POST'])
@admin_required
def aprobar_perfil(perfil_id):
    actualizar_perfil(perfil_id, estado='aprobado')
    flash('Perfil aprobado', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/perfil/<int:perfil_id>/rechazar', methods=['POST'])
@admin_required
def rechazar_perfil(perfil_id):
    actualizar_perfil(perfil_id, estado='rechazado')
    flash('Perfil rechazado', 'warning')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/perfil/<int:perfil_id>/eliminar', methods=['POST'])
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
                        current_app.static_folder, 'usuarios', perfil['slug']
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

    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/perfil/<int:perfil_id>/revisar', methods=['GET', 'POST'])
@admin_required
def revisar_perfil(perfil_id):
    # Obtener el perfil completo (con habilidades, formacion, idiomas)
    conn = get_db_connection()
    perfil = None
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT p.*, cp.nombre AS programa_nombre
                       FROM perfiles p
                       LEFT JOIN catalogo_programas cp ON cp.id = p.programa_id
                       WHERE p.id = %s""",
                    (perfil_id,)
                )
                perfil = cursor.fetchone()
                if perfil:
                    perfil['habilidades'] = _obtener_habilidades(cursor, perfil_id)
                    perfil['formacion'] = _obtener_formacion(cursor, perfil_id)
                    perfil['idiomas'] = _obtener_idiomas(cursor, perfil_id)
        finally:
            conn.close()

    if not perfil:
        abort(404)

    if request.method == 'POST':
        revisiones_dict = {}
        for campo in CAMPOS_REVISABLES:
            estado = request.form.get(f'revision_estado_{campo}', '').strip()
            comentario = request.form.get(f'revision_comentario_{campo}', '').strip()
            # Solo guardar si se seleccionó un estado válido
            if estado in ('aprobado', 'rechazado'):
                revisiones_dict[campo] = {
                    'estado': estado,
                    'comentario': comentario
                }

        comentario_general = request.form.get('comentario_general', '').strip()
        ok = guardar_revisiones(perfil_id, revisiones_dict, comentario_general)
        if ok:
            flash('Revisión guardada correctamente.', 'success')
        else:
            flash('Error al guardar la revisión. Revisa la consola del servidor.', 'error')
        return redirect(url_for('admin.admin_panel'))

    revisiones = obtener_revisiones_perfil(perfil_id)
    imagen = obtener_ruta_imagen_perfil(perfil['slug'])
    return render_template('admin/revisar_perfil.html',
                           perfil=perfil,
                           revisiones=revisiones,
                           imagen=imagen,
                           campos_revisables=CAMPOS_REVISABLES)


# ========================================
# RUTAS: CONTACTOS (ADMIN)
# ========================================

@admin_bp.route('/contactos')
@admin_required
def admin_contactos():
    # Leer filtros del query string
    filtro_estado = request.args.get('estado', '').strip()
    filtro_busqueda = request.args.get('busqueda', '').strip()
    filtro_desde = request.args.get('desde', '').strip()
    filtro_hasta = request.args.get('hasta', '').strip()

    estados_validos = {'nuevo', 'contactado', 'en_proceso', 'cerrado'}

    conn = get_db_connection()
    contactos = []
    total_sin_filtro = 0
    if conn:
        try:
            with conn.cursor() as cursor:
                # Contar total sin filtros
                cursor.execute("SELECT COUNT(*) AS total FROM contactos")
                total_sin_filtro = cursor.fetchone()['total']

                # Construir query con filtros dinámicos
                condiciones = []
                params = []

                if filtro_estado and filtro_estado in estados_validos:
                    condiciones.append("estado_contacto = %s")
                    params.append(filtro_estado)

                if filtro_busqueda:
                    condiciones.append("(nombre LIKE %s OR empresa LIKE %s)")
                    params.append(f'%{filtro_busqueda}%')
                    params.append(f'%{filtro_busqueda}%')

                if filtro_desde:
                    condiciones.append("DATE(fecha_registro) >= %s")
                    params.append(filtro_desde)

                if filtro_hasta:
                    condiciones.append("DATE(fecha_registro) <= %s")
                    params.append(filtro_hasta)

                where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
                cursor.execute(
                    f"SELECT * FROM contactos {where} ORDER BY fecha_registro DESC",
                    params
                )
                contactos = cursor.fetchall()

                # Para cada contacto obtener los practicantes vinculados
                for c in contactos:
                    cursor.execute(
                        """SELECT p.nombre, p.titulo
                           FROM contacto_practicantes cp
                           JOIN perfiles p ON p.id = cp.perfil_id
                           WHERE cp.contacto_id = %s
                           ORDER BY p.nombre ASC""",
                        (c['id'],)
                    )
                    c['practicantes'] = cursor.fetchall()

        finally:
            conn.close()

    filtros = {
        'estado': filtro_estado,
        'busqueda': filtro_busqueda,
        'desde': filtro_desde,
        'hasta': filtro_hasta,
    }

    return render_template(
        'admin/contactos.html',
        contactos=contactos,
        total_sin_filtro=total_sin_filtro,
        filtros=filtros
    )


@admin_bp.route('/contactos/<int:id>/eliminar', methods=['POST'])
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
    return redirect(url_for('admin.admin_contactos'))


@admin_bp.route('/contactos/<int:id>/estado', methods=['POST'])
@admin_required
def actualizar_estado_contacto(id):
    estados_validos = {'nuevo', 'contactado', 'en_proceso', 'cerrado'}
    nuevo_estado = request.form.get('nuevo_estado', '').strip()

    if nuevo_estado not in estados_validos:
        flash('Estado no válido', 'error')
        return redirect(url_for('admin.admin_contactos'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE contactos SET estado_contacto = %s WHERE id = %s",
                    (nuevo_estado, id)
                )
                conn.commit()
            flash('Estado actualizado', 'success')
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
            conn.rollback()
            flash('Error al actualizar el estado', 'error')
        finally:
            conn.close()

    # Preservar filtros del referrer
    referrer = request.referrer or ''
    from urllib.parse import urlparse
    parsed = urlparse(referrer)
    qs = parsed.query
    return redirect(url_for('admin.admin_contactos') + (('?' + qs) if qs else ''))


@admin_bp.route('/contactos/<int:id>/notas', methods=['POST'])
@admin_required
def actualizar_notas_contacto(id):
    notas = request.form.get('notas', '').strip()

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE contactos SET notas_admin = %s WHERE id = %s",
                    (notas, id)
                )
                conn.commit()
            flash('Notas guardadas', 'success')
        except Exception as e:
            print(f"Error al guardar notas: {e}")
            conn.rollback()
            flash('Error al guardar las notas', 'error')
        finally:
            conn.close()

    return redirect(url_for('admin.admin_contactos'))


@admin_bp.route('/contactos/exportar')
@admin_required
def exportar_contactos():
    # Usar los mismos filtros que la vista principal
    filtro_estado = request.args.get('estado', '').strip()
    filtro_busqueda = request.args.get('busqueda', '').strip()
    filtro_desde = request.args.get('desde', '').strip()
    filtro_hasta = request.args.get('hasta', '').strip()

    estados_validos = {'nuevo', 'contactado', 'en_proceso', 'cerrado'}

    conn = get_db_connection()
    contactos = []
    if conn:
        try:
            with conn.cursor() as cursor:
                condiciones = []
                params = []

                if filtro_estado and filtro_estado in estados_validos:
                    condiciones.append("estado_contacto = %s")
                    params.append(filtro_estado)

                if filtro_busqueda:
                    condiciones.append("(nombre LIKE %s OR empresa LIKE %s)")
                    params.append(f'%{filtro_busqueda}%')
                    params.append(f'%{filtro_busqueda}%')

                if filtro_desde:
                    condiciones.append("DATE(fecha_registro) >= %s")
                    params.append(filtro_desde)

                if filtro_hasta:
                    condiciones.append("DATE(fecha_registro) <= %s")
                    params.append(filtro_hasta)

                where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
                cursor.execute(
                    f"SELECT * FROM contactos {where} ORDER BY fecha_registro DESC",
                    params
                )
                contactos = cursor.fetchall()

                # Obtener practicantes vinculados para cada contacto
                for c in contactos:
                    cursor.execute(
                        """SELECT p.nombre FROM contacto_practicantes cp
                           JOIN perfiles p ON p.id = cp.perfil_id
                           WHERE cp.contacto_id = %s ORDER BY p.nombre ASC""",
                        (c['id'],)
                    )
                    rows = cursor.fetchall()
                    c['_practicantes_str'] = ', '.join(r['nombre'] for r in rows)

        finally:
            conn.close()

    output = io.StringIO()
    output.write('\ufeff')  # BOM para compatibilidad con Excel
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(['Nombre', 'Empresa', 'Correo', 'Celular', 'Mensaje', 'Estado', 'Notas', 'Practicantes de interés', 'Fecha'])
    for c in contactos:
        fecha = c['fecha_registro'].strftime('%d/%m/%Y %H:%M') if c.get('fecha_registro') else ''
        writer.writerow([
            c.get('nombre', ''),
            c.get('empresa', ''),
            c.get('correo', ''),
            c.get('celular', ''),
            c.get('mensaje', ''),
            c.get('estado_contacto', 'nuevo'),
            c.get('notas_admin', ''),
            c.get('_practicantes_str', ''),
            fecha
        ])

    nombre_archivo = f"contactos_{date.today().isoformat()}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{nombre_archivo}"'}
    )


# ========================================
# RUTAS: USUARIOS (ADMIN)
# ========================================

@admin_bp.route('/usuarios')
@admin_required
def admin_usuarios():
    usuarios = obtener_todos_usuarios()
    return render_template('admin/usuarios.html', usuarios=usuarios)


@admin_bp.route('/usuarios/<int:user_id>/resetear-password', methods=['POST'])
@admin_required
def resetear_password_usuario(user_id):
    nueva_password = request.form.get('nueva_password', '').strip()

    # Validación backend
    if len(nueva_password) < 8:
        flash('La contraseña debe tener al menos 8 caracteres.', 'error')
        return redirect(url_for('admin.admin_usuarios'))

    # Obtener email para el mensaje de éxito
    usuario = Usuario.obtener_por_id(user_id)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('admin.admin_usuarios'))

    ok = resetear_password(user_id, nueva_password)
    if ok:
        flash(f'Contraseña restablecida para {usuario.email}.', 'success')
    else:
        flash('Error al restablecer la contraseña.', 'error')
    return redirect(url_for('admin.admin_usuarios'))
