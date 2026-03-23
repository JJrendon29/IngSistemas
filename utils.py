import os
import re
import shutil
from functools import wraps

from flask import abort, current_app
from flask_login import login_required, current_user


# ========================================
# HELPERS: SLUG
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


# ========================================
# HELPERS: VALIDACIÓN DE URLs
# ========================================

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


# ========================================
# HELPERS: ARCHIVOS DE PERFIL
# ========================================

def guardar_archivo_perfil(perfil_slug, archivo, tipo):
    """
    Guarda foto o CV en static/usuarios/<slug>/
    tipo: 'foto' o 'cv'
    Retorna la ruta relativa guardada o None
    """
    if not archivo or not archivo.filename:
        return None

    usuario_dir = os.path.join(current_app.static_folder, 'usuarios', perfil_slug)
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
    usuario_dir = os.path.join(current_app.static_folder, 'usuarios', perfil_slug)
    for ext in ('jpg', 'jpeg', 'png'):
        if os.path.exists(os.path.join(usuario_dir, f'perfil.{ext}')):
            return f'usuarios/{perfil_slug}/perfil.{ext}'
    return None


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
