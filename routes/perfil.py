import os
import shutil

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user

from models import (
    obtener_perfil_por_usuario,
    crear_perfil,
    actualizar_perfil,
    guardar_habilidades,
    guardar_formacion,
    guardar_idiomas,
    obtener_catalogo_titulos,
    obtener_catalogo_habilidades,
    obtener_catalogo_idiomas,
    obtener_catalogo_programas,
    obtener_revisiones_perfil,
    resetear_revisiones_pendientes,
)
from utils import generar_slug, validar_urls_perfil, guardar_archivo_perfil
from routes.auth import verificar_linkedin

perfil_bp = Blueprint('perfil', __name__)


# ========================================
# HELPERS PRIVADOS: PARSEAR FORMULARIOS
# ========================================

def _guardar_habilidades_desde_form(perfil_id, form):
    """
    Parsea habilidades del formulario con checkboxes de catálogo.
    Los checkboxes envían catalogo_ids[] con los IDs seleccionados.
    El nivel de cada uno viene en hab_nivel_<catalogo_id>.
    """
    niveles_validos = {'basico', 'intermedio', 'avanzado'}
    catalogo_ids = form.getlist('catalogo_ids[]')
    habilidades = []
    for cid in catalogo_ids:
        try:
            cid_int = int(cid)
        except (ValueError, TypeError):
            continue
        nivel = form.get(f'hab_nivel_{cid_int}', 'intermedio').strip()
        if nivel not in niveles_validos:
            nivel = 'intermedio'
        habilidades.append({'catalogo_id': cid_int, 'nivel': nivel})
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
            # Leer año inicio
            anio_inicio_raw = form.get(f'form_anio_inicio_{i}', '').strip()
            try:
                anio_inicio = int(anio_inicio_raw) if anio_inicio_raw else None
            except ValueError:
                anio_inicio = None

            # Leer en_curso (checkbox: 'on' si marcado)
            en_curso = form.get(f'form_en_curso_{i}', '') == 'on'

            # Leer año fin (solo si no está en curso)
            if en_curso:
                anio_fin = None
            else:
                anio_fin_raw = form.get(f'form_anio_fin_{i}', '').strip()
                try:
                    anio_fin = int(anio_fin_raw) if anio_fin_raw else None
                except ValueError:
                    anio_fin = None

            formaciones.append({
                'titulo': titulo,
                'institucion': form.get(f'form_institucion_{i}', '').strip(),
                'anio_inicio': anio_inicio,
                'anio_fin': anio_fin,
                'en_curso': en_curso,
            })
        i += 1
        if i > 20:
            break
    guardar_formacion(perfil_id, formaciones)


def _guardar_idiomas_desde_form(perfil_id, form):
    """
    Parsea idiomas del formulario dinámico con catálogo.
    Cada fila envía idioma_catalogo_id_<i> y idioma_nivel_<i>.
    Itera hasta que no encuentre ninguna clave más en el form.
    """
    niveles_validos = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Nativo'}
    idiomas_list = []
    # Recopilar todos los índices presentes en el form
    indices = set()
    for key in form.keys():
        if key.startswith('idioma_catalogo_id_'):
            try:
                indices.add(int(key.replace('idioma_catalogo_id_', '')))
            except ValueError:
                pass
    for i in sorted(indices):
        cid = form.get(f'idioma_catalogo_id_{i}', '').strip()
        nivel = form.get(f'idioma_nivel_{i}', '').strip()
        if not cid:
            continue
        try:
            cid_int = int(cid)
        except (ValueError, TypeError):
            continue
        if nivel in niveles_validos:
            idiomas_list.append({'catalogo_id': cid_int, 'nivel': nivel})
    guardar_idiomas(perfil_id, idiomas_list)


# ========================================
# RUTAS: PANEL DEL ESTUDIANTE
# ========================================

@perfil_bp.route('/mi-perfil')
@login_required
def mi_perfil():
    perfil = obtener_perfil_por_usuario(current_user.id)
    revisiones = obtener_revisiones_perfil(perfil['id']) if perfil else {}
    return render_template('mi_perfil.html', perfil=perfil, revisiones=revisiones)


@perfil_bp.route('/mi-perfil/crear', methods=['GET', 'POST'])
@login_required
def crear_mi_perfil():
    # Verificar que no tenga perfil ya
    perfil_existente = obtener_perfil_por_usuario(current_user.id)
    if perfil_existente:
        return redirect(url_for('perfil.editar_mi_perfil'))

    catalogos = {
        'titulos': obtener_catalogo_titulos(),
        'habilidades': obtener_catalogo_habilidades(),
        'idiomas': obtener_catalogo_idiomas(),
        'programas': obtener_catalogo_programas(),
    }

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template('editar_perfil.html', perfil=None, modo='crear',
                                   catalogos=catalogos,
                                   github_session=session.get('github_url', ''),
                                   github_verificado_session=session.get('github_verificado', False))

        slug = generar_slug(nombre)

        # GitHub solo se asigna vía OAuth; no se lee del formulario
        linkedin = request.form.get('linkedin', '').strip()

        errores_url = validar_urls_perfil('', linkedin)
        if errores_url:
            for error in errores_url:
                flash(error, 'error')
            return render_template('editar_perfil.html', perfil=None, modo='crear',
                                   catalogos=catalogos,
                                   github_session=session.get('github_url', ''),
                                   github_verificado_session=session.get('github_verificado', False))

        # Verificar LinkedIn si se proporcionó URL
        linkedin_verificado = False
        if linkedin:
            if verificar_linkedin(linkedin):
                linkedin_verificado = True
            else:
                flash('No se pudo verificar la URL de LinkedIn (el perfil puede ser privado o la URL incorrecta). Se guardará sin verificar.', 'warning')

        # Procesar título: puede ser ID del catálogo o "otro"
        titulo_sel = request.form.get('titulo_catalogo', '').strip()
        titulo_otro = request.form.get('titulo_otro', '').strip()
        if titulo_sel == 'otro':
            titulo_final = titulo_otro
            titulo_otro_guardar = titulo_otro
        else:
            titulo_final = titulo_sel  # Se guarda el id como referencia textual
            titulo_otro_guardar = ''

        # Recuperar GitHub de sesión si el usuario lo vinculó antes de guardar
        github_desde_sesion = session.get('github_url', '')

        # Programa académico actual
        programa_id_raw = request.form.get('programa_id', '').strip()
        try:
            programa_id = int(programa_id_raw) if programa_id_raw else None
        except (ValueError, TypeError):
            programa_id = None
        semestre_raw = request.form.get('semestre_actual', '').strip()
        try:
            semestre_actual = int(semestre_raw) if semestre_raw else None
        except (ValueError, TypeError):
            semestre_actual = None

        perfil_id = crear_perfil(
            usuario_id=current_user.id,
            nombre=nombre,
            slug=slug,
            titulo=titulo_final,
            titulo_otro=titulo_otro_guardar,
            descripcion=request.form.get('descripcion', '').strip(),
            email_contacto=request.form.get('email_contacto', '').strip(),
            github=github_desde_sesion,
            linkedin=linkedin,
            programa_id=programa_id,
            semestre_actual=semestre_actual
        )

        if perfil_id:
            # Guardar estado de verificación de LinkedIn si aplica
            if linkedin_verificado:
                actualizar_perfil(perfil_id, linkedin_verificado=True, estado='pendiente')

            # Persistir verificación de GitHub si vino de sesión
            if github_desde_sesion:
                actualizar_perfil(perfil_id, github_verificado=True, estado='pendiente')
                session.pop('github_url', None)
                session.pop('github_verificado', None)

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

            _guardar_habilidades_desde_form(perfil_id, request.form)
            _guardar_formacion_desde_form(perfil_id, request.form)
            _guardar_idiomas_desde_form(perfil_id, request.form)

            flash('Perfil creado. Está pendiente de aprobación por el administrador.', 'success')
            return redirect(url_for('perfil.mi_perfil'))
        else:
            flash('Error al crear el perfil', 'error')

    return render_template('editar_perfil.html', perfil=None, modo='crear',
                           catalogos=catalogos, revisiones=None,
                           github_session=session.get('github_url', ''),
                           github_verificado_session=session.get('github_verificado', False))


@perfil_bp.route('/mi-perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_mi_perfil():
    perfil = obtener_perfil_por_usuario(current_user.id)
    if not perfil:
        return redirect(url_for('perfil.crear_mi_perfil'))

    catalogos = {
        'titulos': obtener_catalogo_titulos(),
        'habilidades': obtener_catalogo_habilidades(),
        'idiomas': obtener_catalogo_idiomas(),
        'programas': obtener_catalogo_programas(),
    }

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre es obligatorio', 'error')
            return render_template('editar_perfil.html', perfil=perfil, modo='editar',
                                   catalogos=catalogos,
                                   github_session=session.get('github_url', ''),
                                   github_verificado_session=session.get('github_verificado', False))

        nuevo_slug = generar_slug(nombre)

        # Si cambió el slug, renombrar carpeta de archivos
        if nuevo_slug != perfil['slug']:
            old_dir = os.path.join(current_app.static_folder, 'usuarios', perfil['slug'])
            new_dir = os.path.join(current_app.static_folder, 'usuarios', nuevo_slug)
            if os.path.exists(old_dir):
                shutil.move(old_dir, new_dir)

        # GitHub solo se actualiza vía OAuth; preservar el valor actual
        linkedin = request.form.get('linkedin', '').strip()

        errores_url = validar_urls_perfil('', linkedin)
        if errores_url:
            for error in errores_url:
                flash(error, 'error')
            return render_template('editar_perfil.html', perfil=perfil, modo='editar',
                                   catalogos=catalogos,
                                   github_session=session.get('github_url', ''),
                                   github_verificado_session=session.get('github_verificado', False))

        # Determinar estado de verificación de LinkedIn
        linkedin_anterior = perfil.get('linkedin', '') or ''
        if linkedin and linkedin != linkedin_anterior:
            # URL cambió: re-verificar y resetear
            if verificar_linkedin(linkedin):
                linkedin_verificado = True
            else:
                linkedin_verificado = False
                flash('No se pudo verificar la URL de LinkedIn (el perfil puede ser privado o la URL incorrecta). Se guardará sin verificar.', 'warning')
        elif linkedin and linkedin == linkedin_anterior:
            # URL no cambió: mantener el estado actual
            linkedin_verificado = bool(perfil.get('linkedin_verificado'))
        else:
            # Se borró el LinkedIn
            linkedin_verificado = False

        # Procesar título: puede ser ID del catálogo o "otro"
        titulo_sel = request.form.get('titulo_catalogo', '').strip()
        titulo_otro = request.form.get('titulo_otro', '').strip()
        if titulo_sel == 'otro':
            titulo_final = titulo_otro
            titulo_otro_guardar = titulo_otro
        else:
            titulo_final = titulo_sel
            titulo_otro_guardar = ''

        # Si hay GitHub en sesión (recién autorizado), aplicarlo ahora
        github_desde_sesion = session.get('github_url', '')

        # Programa académico actual
        programa_id_raw = request.form.get('programa_id', '').strip()
        try:
            programa_id = int(programa_id_raw) if programa_id_raw else None
        except (ValueError, TypeError):
            programa_id = None
        semestre_raw = request.form.get('semestre_actual', '').strip()
        try:
            semestre_actual = int(semestre_raw) if semestre_raw else None
        except (ValueError, TypeError):
            semestre_actual = None

        kwargs_actualizar = dict(
            nombre=nombre,
            slug=nuevo_slug,
            titulo=titulo_final,
            titulo_otro=titulo_otro_guardar,
            descripcion=request.form.get('descripcion', '').strip(),
            email_contacto=request.form.get('email_contacto', '').strip(),
            linkedin=linkedin,
            linkedin_verificado=linkedin_verificado,
            programa_id=programa_id,
            semestre_actual=semestre_actual,
            # github NO se pasa por defecto: se preserva el valor actual en BD
        )

        if github_desde_sesion:
            kwargs_actualizar['github'] = github_desde_sesion
            kwargs_actualizar['github_verificado'] = True

        actualizar_perfil(perfil['id'], **kwargs_actualizar)

        if github_desde_sesion:
            session.pop('github_url', None)
            session.pop('github_verificado', None)

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

        # Los campos rechazados vuelven a pendiente porque el estudiante los corrigió
        resetear_revisiones_pendientes(perfil['id'])

        flash('Perfil actualizado. Está pendiente de aprobación.', 'success')
        return redirect(url_for('perfil.mi_perfil'))

    revisiones = obtener_revisiones_perfil(perfil['id'])
    return render_template('editar_perfil.html', perfil=perfil, modo='editar',
                           catalogos=catalogos, revisiones=revisiones,
                           github_session=session.get('github_url', ''),
                           github_verificado_session=session.get('github_verificado', False))
