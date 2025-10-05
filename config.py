import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """
    Clase de configuración para la aplicación Flask
    """
    # Clave secreta para Flask (sesiones, cookies, etc.)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración general
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuración de Flask
    TEMPLATES_AUTO_RELOAD = True
    
    # Tamaño máximo de archivos (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024