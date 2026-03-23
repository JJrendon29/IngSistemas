import math
from datetime import datetime

import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import current_user

from db_connection import get_db_connection
from models import (
    obtener_todos_perfiles,
    obtener_perfil_por_slug,
    buscar_perfiles,
    obtener_habilidades_unicas,
    obtener_titulos_unicos,
    obtener_idiomas_unicos,
)
from utils import obtener_ruta_imagen_perfil

public_bp = Blueprint('public', __name__)

PER_PAGE = 12


# ========================================
# RUTA: PÁGINA PRINCIPAL
# ========================================

@public_bp.route('/')
def index():
    filtro_habilidad = request.args.get('habilidad', '').strip()
    filtro_titulo = request.args.get('titulo', '').strip()
    filtro_idioma = request.args.get('idioma', '').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            page = 1
    except (ValueError, TypeError):
        page = 1

    hay_filtros = bool(filtro_titulo or filtro_habilidad or filtro_idioma)

    if hay_filtros:
        perfiles, total = buscar_perfiles(
            titulo=filtro_titulo,
            habilidad=filtro_habilidad,
            idioma=filtro_idioma,
            page=page,
            per_page=PER_PAGE
        )
    else:
        perfiles, total = obtener_todos_perfiles(solo_aprobados=True, page=page, per_page=PER_PAGE)

    total_pages = math.ceil(total / PER_PAGE) if total > 0 else 1

    habilidades_disponibles = obtener_habilidades_unicas()
    titulos = obtener_titulos_unicos()
    idiomas = obtener_idiomas_unicos()

    return render_template('index.html',
                           perfiles=perfiles,
                           habilidades_disponibles=habilidades_disponibles,
                           titulos=titulos,
                           idiomas=idiomas,
                           filtro_habilidad=filtro_habilidad,
                           filtro_titulo=filtro_titulo,
                           filtro_idioma=filtro_idioma,
                           page=page,
                           total_pages=total_pages,
                           total=total)


# ========================================
# RUTA: VER PERFIL PÚBLICO
# ========================================

@public_bp.route('/perfil/<slug>')
def ver_perfil(slug):
    perfil = obtener_perfil_por_slug(slug, solo_aprobados=True)
    if perfil is None:
        abort(404)
    # Verificar imagen en disco
    perfil['_imagen_disco'] = obtener_ruta_imagen_perfil(slug)
    return render_template('perfil.html', perfil=perfil)


# ========================================
# RUTAS: CONTACTO
# ========================================

@public_bp.route('/contacto')
def contacto():
    perfiles_aprobados = []
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT id, nombre, titulo FROM perfiles WHERE estado = 'aprobado' ORDER BY nombre ASC"
                )
                perfiles_aprobados = cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener perfiles aprobados: {e}")
        finally:
            conn.close()
    return render_template('contacto.html', perfiles_aprobados=perfiles_aprobados)


@public_bp.route('/guardar_contacto', methods=['POST'])
def guardar_contacto():
    try:
        nombre = request.form.get('nombre', '').strip()
        empresa = request.form.get('empresa', '').strip()
        correo = request.form.get('correo', '').strip()
        celular = request.form.get('celular', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        practicantes_ids = request.form.getlist('practicantes_ids[]')

        if not all([nombre, empresa, correo, celular]):
            flash('Por favor completa todos los campos obligatorios', 'error')
            return redirect(url_for('public.contacto'))

        conn = get_db_connection()
        if conn is None:
            flash('Error al conectar con la base de datos', 'error')
            return redirect(url_for('public.contacto'))

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO contactos (nombre, empresa, correo, celular, mensaje, fecha_registro)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (nombre, empresa, correo, celular, mensaje, datetime.now())
                )
                contacto_id = cursor.lastrowid

                # Guardar practicantes de interés si los hay
                for pid in practicantes_ids:
                    try:
                        pid_int = int(pid)
                    except (ValueError, TypeError):
                        continue
                    cursor.execute(
                        "INSERT INTO contacto_practicantes (contacto_id, perfil_id) VALUES (%s, %s)",
                        (contacto_id, pid_int)
                    )

                conn.commit()
        finally:
            conn.close()

        flash('¡Mensaje enviado exitosamente!', 'success')
        return redirect(url_for('public.contacto'))

    except Exception as e:
        print(f"Error al guardar contacto: {e}")
        flash('Error al guardar el contacto', 'error')
        return redirect(url_for('public.contacto'))


# ========================================
# RUTA: API INSTITUCIONES
# ========================================

@public_bp.route('/api/instituciones')
def api_instituciones():
    """
    Consulta la API de Datos Abiertos Colombia para autocompletar nombres de colegios.
    Recibe: ?q=<texto>
    Retorna: JSON con lista de nombres de establecimientos educativos.
    """
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])

    try:
        url = 'https://www.datos.gov.co/resource/upkm-vdjb.json'
        params = {
            '$where': f"upper(nombreestablecimiento) like upper('%{q}%')",
            '$limit': 15,
            '$select': 'nombreestablecimiento,nombremunicipio,nombredepartamento',
            '$order': 'nombreestablecimiento'
        }
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        # Extraer nombres únicos, eliminar None y valores vacíos
        nombres = list({
            item['nombreestablecimiento'].strip()
            for item in data
            if item.get('nombreestablecimiento', '').strip()
        })
        nombres.sort()
        return jsonify(nombres)
    except requests.exceptions.Timeout:
        return jsonify([])
    except Exception as e:
        print(f"Error consultando API de instituciones: {e}")
        return jsonify([])
