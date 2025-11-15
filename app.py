"""
╔════════════════════════════════════════════════════════════════════════════╗
║     UNIPAZ QUIZ SYSTEM - app.py COMPLETO FINAL v5                        ║
║     CON TABLA resultados_quizes + estadisticas_por_modo                  ║
║     CON RANKINGS GLOBALES, POR CARRERA, Y POR MODO                       ║
║     FECHA: 2025-11-15                                                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# ===== INICIALIZAR FLASK =====
app = Flask(__name__, template_folder='templates', static_folder='static')

# ===== CONFIGURACIÓN =====
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1606@localhost:3306/unipaz_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['JSON_SORT_KEYS'] = False

# ===== DB Y CORS =====
db = SQLAlchemy(app)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════
# ===== MODELOS =====
# ═══════════════════════════════════════════════════════════════════════════

class Carrera(db.Model):
    __tablename__ = 'carreras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(50))
    color = db.Column(db.String(7))


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'))
    racha_actual = db.Column(db.Integer, default=0)
    racha_maxima = db.Column(db.Integer, default=0)
    total_puntos = db.Column(db.Integer, default=0)
    preguntas_correctas = db.Column(db.Integer, default=0)
    preguntas_totales = db.Column(db.Integer, default=0)


class Materia(db.Model):
    __tablename__ = 'materias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    semestre = db.Column(db.Integer)
    profesor = db.Column(db.String(150))
    descripcion = db.Column(db.Text)


class Pregunta(db.Model):
    __tablename__ = 'preguntas'
    id = db.Column(db.Integer, primary_key=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    opcion_a = db.Column(db.String(500))
    opcion_b = db.Column(db.String(500))
    opcion_c = db.Column(db.String(500))
    opcion_d = db.Column(db.String(500))
    respuesta_correcta = db.Column(db.String(1))
    dificultad = db.Column(db.String(20), default='medio')
    activo = db.Column(db.Boolean, default=True)


class Examen(db.Model):
    __tablename__ = 'examenes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    descripcion = db.Column(db.Text)
    duracion_minutos = db.Column(db.Integer, default=60)
    contraseña = db.Column(db.String(100))
    codigo_acceso = db.Column(db.String(50), unique=True)
    permitir_repaso = db.Column(db.Boolean, default=True)
    mostrar_puntaje_inmediato = db.Column(db.Boolean, default=True)
    permitir_volver_atras = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)


class ExamenPregunta(db.Model):
    __tablename__ = 'examen_preguntas'
    id = db.Column(db.Integer, primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    orden = db.Column(db.Integer, default=0)
    puntos = db.Column(db.Integer, default=1)


class ResultadoExamen(db.Model):
    __tablename__ = 'resultados_examenes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=True)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    preguntas_totales = db.Column(db.Integer, default=0)
    preguntas_correctas = db.Column(db.Integer, default=0)
    puntos_obtenidos = db.Column(db.Integer, default=0)
    porcentaje = db.Column(db.Float, default=0.0)
    tiempo_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    tiempo_fin = db.Column(db.DateTime)
    tiempo_total_segundos = db.Column(db.Integer, default=0)
    modo = db.Column(db.String(20), default='normal')
    fecha_examen = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='completado')
    observaciones = db.Column(db.Text)


class ResultadoQuiz(db.Model):
    __tablename__ = 'resultados_quizes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey('materias.id'), nullable=False)
    preguntas_totales = db.Column(db.Integer, default=0)
    preguntas_correctas = db.Column(db.Integer, default=0)
    puntos_obtenidos = db.Column(db.Integer, default=0)
    porcentaje = db.Column(db.Float, default=0.0)
    tiempo_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    tiempo_fin = db.Column(db.DateTime)
    tiempo_total_segundos = db.Column(db.Integer, default=0)
    modo = db.Column(db.String(20), default='normal')
    fecha_quiz = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='completado')
    observaciones = db.Column(db.Text)


class EstadisticaPorModo(db.Model):
    __tablename__ = 'estadisticas_por_modo'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    modo = db.Column(db.String(20), nullable=False)
    
    total_puntos = db.Column(db.Integer, default=0)
    total_respuestas_correctas = db.Column(db.Integer, default=0)
    total_respuestas = db.Column(db.Integer, default=0)
    
    intentos = db.Column(db.Integer, default=0)
    
    mejor_puntuacion = db.Column(db.Integer, default=0)
    mejor_porcentaje = db.Column(db.Float, default=0.0)
    
    promedio_puntos = db.Column(db.Float, default=0.0)
    promedio_porcentaje = db.Column(db.Float, default=0.0)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('usuario_id', 'modo', name='unique_usuario_modo'),)


# ═══════════════════════════════════════════════════════════════════════════
# ===== FUNCIONES HELPER =====
# ═══════════════════════════════════════════════════════════════════════════

def hashear_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_password(password, password_hash):
    return hashear_password(password) == password_hash


# ═══════════════════════════════════════════════════════════════════════════
# ===== RUTAS FRONTEND =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/rankings')
def rankings():
    return render_template('rankings.html')

@app.route('/perfil')
def perfil():
    return render_template('perfil.html')


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - AUTENTICACIÓN =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if not usuario or not verificar_password(password, usuario.password_hash):
            return jsonify({'error': 'Email o contraseña incorrectos'}), 401
        
        return jsonify({
            'success': True,
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'email': usuario.email,
                'carrera_id': usuario.carrera_id
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        email = data.get('email')
        password = data.get('password')
        carrera_id = data.get('carrera_id')
        
        if not all([nombre, email, password, carrera_id]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash=hashear_password(password),
            carrera_id=carrera_id
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'usuario': {
                'id': nuevo_usuario.id,
                'nombre': nuevo_usuario.nombre,
                'email': nuevo_usuario.email
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - CARRERAS Y MATERIAS =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/carreras', methods=['GET'])
def get_carreras():
    try:
        carreras = Carrera.query.all()
        resultado = [{'id': c.id, 'nombre': c.nombre, 'icono': c.icono, 'color': c.color, 'descripcion': c.descripcion} for c in carreras]
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/materias/<int:carrera_id>', methods=['GET'])
def get_materias_por_carrera(carrera_id):
    try:
        materias = Materia.query.filter_by(carrera_id=carrera_id).order_by(Materia.semestre).all()
        resultado = [{'id': m.id, 'nombre': m.nombre, 'carrera_id': m.carrera_id, 'semestre': m.semestre, 'profesor': m.profesor, 'descripcion': m.descripcion} for m in materias]
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - PREGUNTAS =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/preguntas/<int:materia_id>', methods=['GET'])
def get_preguntas(materia_id):
    try:
        dificultad = request.args.get('dificultad', 'facil')
        cantidad = request.args.get('cantidad', 10, type=int)
        
        preguntas = Pregunta.query.filter_by(materia_id=materia_id, dificultad=dificultad, activo=True).limit(cantidad).all()
        
        if not preguntas:
            preguntas = Pregunta.query.filter_by(materia_id=materia_id, activo=True).limit(cantidad).all()
        
        resultado = [{'id': p.id, 'texto': p.texto, 'opcion_a': p.opcion_a, 'opcion_b': p.opcion_b, 'opcion_c': p.opcion_c, 'opcion_d': p.opcion_d, 'respuesta_correcta': p.respuesta_correcta, 'dificultad': p.dificultad} for p in preguntas]
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - PERFIL DE USUARIO =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/usuarios/<int:usuario_id>/perfil', methods=['GET'])
def obtener_perfil_usuario(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        carrera = Carrera.query.get(usuario.carrera_id) if usuario.carrera_id else None
        
        return jsonify({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'email': usuario.email,
            'carrera': carrera.nombre if carrera else 'Sin carrera',
            'carrera_id': usuario.carrera_id,
            'racha_actual': usuario.racha_actual,
            'racha_maxima': usuario.racha_maxima,
            'total_puntos': usuario.total_puntos,
            'preguntas_correctas': usuario.preguntas_correctas,
            'preguntas_totales': usuario.preguntas_totales,
            'porcentaje_exito': round((usuario.preguntas_correctas / usuario.preguntas_totales * 100) if usuario.preguntas_totales > 0 else 0, 2)
        }), 200
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - GUARDAR RESULTADO DE QUIZ =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/usuarios/<int:usuario_id>/guardar-resultado', methods=['POST'])
def guardar_resultado_quiz(usuario_id):
    try:
        print("\n" + "="*80)
        print("🔴 ENDPOINT: /api/usuarios/" + str(usuario_id) + "/guardar-resultado")
        print("="*80)
        
        data = request.get_json()
        print("📥 DATOS RECIBIDOS:", data)
        
        usuario = Usuario.query.get(usuario_id)
        print("👤 Usuario ID:", usuario_id)
        print("👤 Usuario encontrado:", usuario.nombre if usuario else "NO ENCONTRADO")
        
        if not usuario:
            print("❌ ERROR: Usuario no encontrado")
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        modo = data.get('modo', 'facil').lower()
        print("🎮 MODO:", modo)
        
        # GUARDAR EN resultados_quizes
        nuevo_resultado = ResultadoQuiz(
            usuario_id=usuario_id,
            materia_id=data.get('materia_id'),
            preguntas_totales=data.get('preguntas_totales', 0),
            preguntas_correctas=data.get('preguntas_correctas', 0),
            puntos_obtenidos=data.get('puntos_obtenidos', 0),
            porcentaje=data.get('porcentaje', 0),
            tiempo_total_segundos=data.get('tiempo_total_segundos', 0),
            modo=modo,
            estado='completado'
        )
        
        print("\n💾 GUARDANDO en resultados_quizes:")
        print("  - Puntos:", nuevo_resultado.puntos_obtenidos)
        print("  - Correctas:", nuevo_resultado.preguntas_correctas)
        print("  - Modo:", nuevo_resultado.modo)
        
        db.session.add(nuevo_resultado)
        db.session.flush()
        
        # ACTUALIZAR estadisticas_por_modo
        print("\n🔄 ACTUALIZANDO estadisticas_por_modo:")
        
        estadistica = EstadisticaPorModo.query.filter_by(
            usuario_id=usuario_id,
            modo=modo
        ).first()
        
        if not estadistica:
            print(f"  ✨ Primera vez en modo {modo} - Creando registro")
            estadistica = EstadisticaPorModo(
                usuario_id=usuario_id,
                modo=modo,
                total_puntos=nuevo_resultado.puntos_obtenidos,
                total_respuestas_correctas=nuevo_resultado.preguntas_correctas,
                total_respuestas=nuevo_resultado.preguntas_totales,
                intentos=1,
                mejor_puntuacion=nuevo_resultado.puntos_obtenidos,
                mejor_porcentaje=nuevo_resultado.porcentaje,
                promedio_puntos=float(nuevo_resultado.puntos_obtenidos),
                promedio_porcentaje=float(nuevo_resultado.porcentaje)
            )
            db.session.add(estadistica)
        else:
            print(f"  📊 Actualizando estadísticas del modo {modo}")
            
            estadistica.total_puntos += nuevo_resultado.puntos_obtenidos
            estadistica.total_respuestas_correctas += nuevo_resultado.preguntas_correctas
            estadistica.total_respuestas += nuevo_resultado.preguntas_totales
            
            estadistica.intentos += 1
            
            if nuevo_resultado.puntos_obtenidos > estadistica.mejor_puntuacion:
                estadistica.mejor_puntuacion = nuevo_resultado.puntos_obtenidos
                estadistica.mejor_porcentaje = nuevo_resultado.porcentaje
            
            estadistica.promedio_puntos = estadistica.total_puntos / estadistica.intentos
            estadistica.promedio_porcentaje = (
                estadistica.total_respuestas_correctas / estadistica.total_respuestas * 100 
                if estadistica.total_respuestas > 0 else 0
            )
            
            print(f"  - Total puntos: {estadistica.total_puntos}")
            print(f"  - Total correctas: {estadistica.total_respuestas_correctas}")
            print(f"  - Intentos: {estadistica.intentos}")
            print(f"  - Mejor puntuación: {estadistica.mejor_puntuacion}")
            print(f"  - Promedio: {estadistica.promedio_puntos:.2f}")
        
        # ACTUALIZAR usuario.total_puntos (GENERAL)
        print("\n👤 ACTUALIZANDO USUARIO TOTAL:")
        usuario.total_puntos += nuevo_resultado.puntos_obtenidos
        usuario.preguntas_correctas += nuevo_resultado.preguntas_correctas
        usuario.preguntas_totales += nuevo_resultado.preguntas_totales
        
        print("  - Nuevos puntos totales:", usuario.total_puntos)
        print("  - Nuevas respuestas correctas:", usuario.preguntas_correctas)
        print("  - Nuevas respuestas totales:", usuario.preguntas_totales)
        
        db.session.commit()
        
        print("\n✅ ¡GUARDADO EN BD EXITOSAMENTE!")
        print("   Resultado ID:", nuevo_resultado.id)
        print("="*80 + "\n")
        
        return jsonify({'success': True, 'resultado_id': nuevo_resultado.id}), 201
    except Exception as e:
        db.session.rollback()
        print("\n❌ ERROR FATAL:", str(e))
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== API - RANKINGS =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/rankings/global', methods=['GET'])
def rankings_global():
    try:
        usuarios = Usuario.query.order_by(Usuario.total_puntos.desc()).limit(20).all()
        resultado = []
        
        for idx, u in enumerate(usuarios):
            total_intentos = db.session.query(db.func.sum(EstadisticaPorModo.intentos)).filter_by(
                usuario_id=u.id
            ).scalar() or 0
            
            eficiencia = u.total_puntos / total_intentos if total_intentos > 0 else 0
            porcentaje = round((u.preguntas_correctas / u.preguntas_totales * 100) if u.preguntas_totales > 0 else 0, 2)
            
            resultado.append({
                'posicion': idx + 1,
                'nombre': u.nombre,
                'puntos': u.total_puntos,
                'racha': u.racha_actual,
                'correctas': u.preguntas_correctas,
                'porcentaje': porcentaje,
                'intentos': total_intentos,
                'eficiencia': round(eficiencia, 2)
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/carrera/<int:carrera_id>', methods=['GET'])
def rankings_carrera(carrera_id):
    try:
        usuarios = Usuario.query.filter_by(carrera_id=carrera_id).all()
        if not usuarios:
            return jsonify([]), 200
        
        resultado = []
        usuarios_sorted = sorted(usuarios, key=lambda u: u.total_puntos, reverse=True)
        
        for idx, u in enumerate(usuarios_sorted[:20]):
            total_intentos = db.session.query(db.func.sum(EstadisticaPorModo.intentos)).filter_by(
                usuario_id=u.id
            ).scalar() or 0
            
            eficiencia = u.total_puntos / total_intentos if total_intentos > 0 else 0
            porcentaje = round((u.preguntas_correctas / u.preguntas_totales * 100) if u.preguntas_totales > 0 else 0, 2)
            
            resultado.append({
                'posicion': idx + 1,
                'nombre': u.nombre,
                'puntos': u.total_puntos,
                'racha': u.racha_actual,
                'correctas': u.preguntas_correctas,
                'porcentaje': porcentaje,
                'intentos': total_intentos,
                'eficiencia': round(eficiencia, 2)
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/rankings/por-modo/<modo>', methods=['GET'])
def rankings_por_modo(modo):
    try:
        modo_str = modo.lower()
        
        estadisticas = EstadisticaPorModo.query.filter_by(modo=modo_str).order_by(
            EstadisticaPorModo.promedio_puntos.desc()
        ).limit(20).all()
        
        resultado = []
        for idx, est in enumerate(estadisticas):
            usuario = Usuario.query.get(est.usuario_id)
            if usuario:
                resultado.append({
                    'posicion': idx + 1,
                    'nombre': usuario.nombre,
                    'modo': est.modo,
                    'puntos': est.total_puntos,
                    'correctas': est.total_respuestas_correctas,
                    'intentos': est.intentos,
                    'mejor_puntuacion': est.mejor_puntuacion,
                    'promedio_puntos': round(est.promedio_puntos, 2),
                    'promedio_porcentaje': round(est.promedio_porcentaje, 2)
                })
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/usuarios/<int:usuario_id>/estadisticas-por-modo', methods=['GET'])
def obtener_estadisticas_por_modo(usuario_id):
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        estadisticas = EstadisticaPorModo.query.filter_by(usuario_id=usuario_id).all()
        
        resultado = {
            'usuario_id': usuario_id,
            'usuario_nombre': usuario.nombre,
            'total_puntos_general': usuario.total_puntos,
            'modos': {}
        }
        
        for est in estadisticas:
            resultado['modos'][est.modo] = {
                'total_puntos': est.total_puntos,
                'total_respuestas_correctas': est.total_respuestas_correctas,
                'total_respuestas': est.total_respuestas,
                'intentos': est.intentos,
                'mejor_puntuacion': est.mejor_puntuacion,
                'mejor_porcentaje': round(est.mejor_porcentaje, 2),
                'promedio_puntos': round(est.promedio_puntos, 2),
                'promedio_porcentaje': round(est.promedio_porcentaje, 2)
            }
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== HEALTH CHECK =====
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok', 'database': 'connected', 'message': '✅ Conexión exitosa'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'database': 'disconnected', 'message': f'❌ Error: {str(e)}'}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== ERROR HANDLERS =====
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Error del servidor'}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ===== MAIN =====
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    with app.app_context():
        print("=" * 80)
        print("🚀 UNIPAZ QUIZ SYSTEM - VERSIÓN FINAL v5")
        print("=" * 80)
        print("✅ Base de Datos: unipaz_db")
        print("✅ Usuario BD: root | Contraseña: 1606")
        print("✅ TABLAS:")
        print("   ✓ usuarios")
        print("   ✓ carreras")
        print("   ✓ materias")
        print("   ✓ preguntas")
        print("   ✓ resultados_quizes")
        print("   ✓ estadisticas_por_modo")
        print("=" * 80)
        
        try:
            db.create_all()
            print("✅ Tablas de BD verificadas")
        except Exception as e:
            print(f"❌ Error con BD: {str(e)}")
        
        print("=" * 80)
        print("🌍 Servidor: http://localhost:5000")
        print("=" * 80)
        print("\n✅ CARACTERÍSTICAS:")
        print("   ✓ Login/Registro")
        print("   ✓ Quiz por materia")
        print("   ✓ Guardado en resultados_quizes")
        print("   ✓ Estadísticas por modo (fácil, medio, difícil)")
        print("   ✓ Rankings Global")
        print("   ✓ Rankings por Carrera")
        print("   ✓ Rankings por Modo")
        print("   ✓ Conteo de intentos")
        print("   ✓ Cálculo de eficiencia")
        print("\n" + "=" * 80)
        
        app.run(debug=True, host='0.0.0.0', port=5000)