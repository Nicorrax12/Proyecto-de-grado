from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    # Opción 1: Usar la variable de entorno DATABASE_URL (recomendado para producción)
    database_url = os.environ.get('DATABASE_URL')
    
    # Opción 2: Construir la URL manualmente con tus credenciales
    if not database_url:
        database_url = 'postgresql://fierro_user:epGrnVoxxDNig670zLVbLMrtvL7w6YnT@dpg-d49j04fgi27c73ccikj0-a.oregon-postgres.render.com/fierro'
    
    # Asegurar que la URL use el formato correcto
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
