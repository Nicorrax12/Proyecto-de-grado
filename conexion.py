# conexion.py - Configuración de conexión a PostgreSQL en Render para Flask

from flask_sqlalchemy import SQLAlchemy
import os
from urllib.parse import quote_plus

db = SQLAlchemy()

def init_db(app):
    """
    Inicializa la base de datos PostgreSQL en Render
    Soporta tanto variables de entorno como credenciales directas
    """
    
    # Opción 1: Usar la variable de entorno DATABASE_URL (RECOMENDADO para producción)
    database_url = os.environ.get('DATABASE_URL')
    
    # Opción 2: Construir la URL manualmente con credenciales
    if not database_url:
        # Credenciales para desarrollo/testing
        host = os.environ.get('DB_HOST', 'dpg-d49j04fgi27c73ccikj0-a.oregon-postgres.render.com')
        port = os.environ.get('DB_PORT', '5432')
        database = os.environ.get('DB_NAME', 'fierro')
        user = os.environ.get('DB_USER', 'fierro_user')
        password = os.environ.get('DB_PASSWORD', 'epGrnVoxxDNig670zLVbLMrtvL7w6YnT')
        
        # Escapar caracteres especiales en la contraseña
        password_encoded = quote_plus(password)
        
        database_url = f'postgresql://{user}:{password_encoded}@{host}:{port}/{database}'
    
    # Asegurar que la URL use el formato correcto (postgresql:// en lugar de postgres://)
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Configurar Flask-SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'echo': False
    }
    
    db.init_app(app)
    
    # Crear contexto de aplicación y tablas
    with app.app_context():
        db.create_all()
    
    return db


def get_db():
    """Obtiene la instancia actual de la base de datos"""
    return db
