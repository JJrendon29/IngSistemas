import os

from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import Usuario

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
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Debes iniciar sesión para acceder.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.obtener_por_id(int(user_id))


# ========================================
# REGISTRAR BLUEPRINTS
# ========================================

from routes.auth import auth_bp
from routes.public import public_bp
from routes.perfil import perfil_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(public_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(admin_bp)


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
# ERROR HANDLERS
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
