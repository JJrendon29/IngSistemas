import re

import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user

from models import Usuario, obtener_perfil_por_usuario, actualizar_perfil

auth_bp = Blueprint('auth', __name__)


# ========================================
# HELPER: VERIFICACIÓN DE LINKEDIN
# ========================================

def verificar_linkedin(url):
    """
    Verifica que la URL de LinkedIn sea accesible.
    Retorna True si responde con código 200, False en cualquier otro caso.
    """
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        return resp.status_code == 200
    except Exception:
        return False


# ========================================
# RUTAS: AUTENTICACIÓN
# ========================================

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # Validar dominio institucional
        dominio = current_app.config.get('DOMINIO_INSTITUCIONAL', 'amigo.edu.co')
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
            return redirect(url_for('auth.login'))
        else:
            flash('Error al crear la cuenta', 'error')

    return render_template('registro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        usuario = Usuario.obtener_por_email(email)

        if usuario and usuario.activo and usuario.verificar_password(password):
            login_user(usuario)
            next_page = request.args.get('next')
            flash('Sesión iniciada correctamente', 'success')
            return redirect(next_page or url_for('public.index'))
        else:
            flash('Correo o contraseña incorrectos', 'error')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('public.index'))


# ========================================
# RUTAS: GITHUB OAUTH
# ========================================

@auth_bp.route('/auth/github')
@login_required
def auth_github():
    client_id = current_app.config.get('GITHUB_CLIENT_ID', '')
    if not client_id:
        flash('La integración con GitHub no está configurada.', 'error')
        return redirect(url_for('perfil.editar_mi_perfil'))

    # Si el usuario ya tiene GitHub vinculado (modo "Cambiar cuenta"),
    # limpiar sesión y BD antes de iniciar el flujo OAuth de nuevo
    perfil = obtener_perfil_por_usuario(current_user.id)
    if perfil and perfil.get('github_verificado'):
        session.pop('github_url', None)
        session.pop('github_verificado', None)
        actualizar_perfil(
            perfil['id'],
            github='',
            github_verificado=False,
            estado=perfil['estado']
        )

    redirect_uri = 'http://localhost:5000/auth/github/callback'
    github_url = (
        f'https://github.com/login/oauth/authorize'
        f'?client_id={client_id}'
        f'&redirect_uri={redirect_uri}'
        f'&scope=read:user'
        f'&allow_signup=false'
    )
    return redirect(github_url)


@auth_bp.route('/auth/github/callback')
@login_required
def auth_github_callback():
    code = request.args.get('code', '').strip()
    if not code:
        flash('Error al conectar con GitHub: no se recibió código de autorización.', 'error')
        return redirect(url_for('perfil.editar_mi_perfil'))

    client_id = current_app.config.get('GITHUB_CLIENT_ID', '')
    client_secret = current_app.config.get('GITHUB_CLIENT_SECRET', '')

    try:
        # Intercambiar código por access token
        token_resp = requests.post(
            'https://github.com/login/oauth/access_token',
            json={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
            },
            headers={'Accept': 'application/json'},
            timeout=10
        )
        token_data = token_resp.json()
        access_token = token_data.get('access_token', '')
        if not access_token:
            flash('Error al obtener el token de GitHub. Intenta de nuevo.', 'error')
            return redirect(url_for('perfil.editar_mi_perfil'))

        # Obtener datos del usuario de GitHub
        user_resp = requests.get(
            'https://api.github.com/user',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json',
            },
            timeout=10
        )
        user_data = user_resp.json()
        html_url = user_data.get('html_url', '')
        if not html_url:
            flash('No se pudo obtener la URL de tu perfil de GitHub.', 'error')
            return redirect(url_for('perfil.editar_mi_perfil'))

        # Guardar en sesión: el perfil aún puede no existir (flujo de creación)
        session['github_url'] = html_url
        session['github_verificado'] = True

        flash('GitHub vinculado correctamente. Guarda el formulario para confirmar los cambios.', 'success')

        perfil = obtener_perfil_por_usuario(current_user.id)
        if perfil:
            return redirect(url_for('perfil.editar_mi_perfil'))
        return redirect(url_for('perfil.crear_mi_perfil'))

    except requests.exceptions.Timeout:
        flash('Tiempo de espera agotado al conectar con GitHub. Intenta de nuevo.', 'error')
        return redirect(url_for('perfil.editar_mi_perfil'))
    except Exception as e:
        print(f"Error en GitHub OAuth callback: {e}")
        flash('Error al verificar GitHub. Intenta de nuevo.', 'error')
        return redirect(url_for('perfil.editar_mi_perfil'))
