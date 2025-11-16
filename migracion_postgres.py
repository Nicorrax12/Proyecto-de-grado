# migracion_postgres.py - Script completo de migración MySQL a PostgreSQL en Render

import psycopg2
from psycopg2 import sql
import os
from datetime import datetime
import json

# ============================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================

class ConfiguracionDB:
    """Maneja la configuración de conexión a PostgreSQL"""
    
    def __init__(self):
        # Opción 1: Usar variable de entorno (RECOMENDADO PARA PRODUCCIÓN)
        self.database_url = os.environ.get('DATABASE_URL')
        
        # Opción 2: URL hardcodeada (PARA DESARROLLO/TESTING)
        if not self.database_url:
            self.database_url = 'postgresql://fierro_user:epGrnVoxxDNig670zLVbLMrtvL7w6YnT@dpg-d49j04fgi27c73ccikj0-a.oregon-postgres.render.com/fierro'
        
        # Convertir postgres:// a postgresql://
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return psycopg2.connect(self.database_url)


# ============================================
# SCRIPT DE MIGRACIÓN
# ============================================

def crear_tablas_postgresql(cursor):
    """Crea todas las tablas en PostgreSQL adaptadas del schema MySQL"""
    
    # Tabla: usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            carrera_id INTEGER,
            avatar_url VARCHAR(500),
            nivel INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            racha_actual INTEGER DEFAULT 0,
            racha_maxima INTEGER DEFAULT 0,
            total_puntos INTEGER DEFAULT 0,
            preguntas_correctas INTEGER DEFAULT 0,
            preguntas_totales INTEGER DEFAULT 0,
            rol VARCHAR(20) DEFAULT 'estudiante',
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Tabla: carreras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carreras (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            descripcion TEXT,
            icono VARCHAR(50),
            color VARCHAR(7),
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Añadir constraint de foreign key para usuarios
    cursor.execute("""
        ALTER TABLE usuarios
        ADD CONSTRAINT fk_usuarios_carrera
        FOREIGN KEY (carrera_id) REFERENCES carreras(id)
        ON DELETE SET NULL;
    """)
    
    # Tabla: materias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            carrera_id INTEGER NOT NULL,
            semestre INTEGER,
            profesor VARCHAR(150),
            descripcion TEXT,
            cantidad_preguntas INTEGER DEFAULT 0,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (carrera_id) REFERENCES carreras(id)
        );
    """)
    
    # Tabla: preguntas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preguntas (
            id SERIAL PRIMARY KEY,
            materia_id INTEGER NOT NULL,
            enunciado TEXT NOT NULL,
            opcion_a VARCHAR(500) NOT NULL,
            opcion_b VARCHAR(500) NOT NULL,
            opcion_c VARCHAR(500) NOT NULL,
            opcion_d VARCHAR(500),
            respuesta_correcta CHAR(1) NOT NULL,
            dificultad VARCHAR(20) DEFAULT 'medio',
            explicacion TEXT,
            activa BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        );
    """)
    
    # Tabla: examenes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS examenes (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            materia_id INTEGER NOT NULL,
            creado_por INTEGER,
            descripcion TEXT,
            duracion_minutos INTEGER DEFAULT 60,
            contraseña VARCHAR(100),
            codigo_acceso VARCHAR(50) UNIQUE,
            permitir_repaso BOOLEAN DEFAULT TRUE,
            mostrar_puntaje_inmediato BOOLEAN DEFAULT TRUE,
            permitir_volver_atras BOOLEAN DEFAULT TRUE,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE,
            FOREIGN KEY (creado_por) REFERENCES usuarios(id) ON DELETE SET NULL
        );
    """)
    
    # Tabla: examen_preguntas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS examen_preguntas (
            id SERIAL PRIMARY KEY,
            examen_id INTEGER NOT NULL,
            pregunta_id INTEGER NOT NULL,
            orden INTEGER DEFAULT 0,
            puntos INTEGER DEFAULT 1,
            fecha_agregada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(examen_id, pregunta_id),
            FOREIGN KEY (examen_id) REFERENCES examenes(id) ON DELETE CASCADE,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE
        );
    """)
    
    # Tabla: respuestas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respuestas (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            pregunta_id INTEGER NOT NULL,
            respuesta_dada CHAR(1),
            es_correcta BOOLEAN,
            tiempo_respuesta INTEGER,
            modo VARCHAR(20) DEFAULT 'normal',
            materia_id INTEGER,
            fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id),
            FOREIGN KEY (materia_id) REFERENCES materias(id)
        );
    """)
    
    # Tabla: resultados_examenes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_examenes (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            examen_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            preguntas_totales INTEGER DEFAULT 0,
            preguntas_correctas INTEGER DEFAULT 0,
            puntos_obtenidos INTEGER DEFAULT 0,
            porcentaje FLOAT DEFAULT 0,
            tiempo_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tiempo_fin TIMESTAMP,
            tiempo_total_segundos INTEGER DEFAULT 0,
            modo VARCHAR(20) DEFAULT 'normal',
            fecha_examen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'completado',
            observaciones TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (examen_id) REFERENCES examenes(id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        );
    """)
    
    # Tabla: resultados_quizes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados_quizes (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            preguntas_totales INTEGER DEFAULT 0,
            preguntas_correctas INTEGER DEFAULT 0,
            puntos_obtenidos INTEGER DEFAULT 0,
            porcentaje FLOAT DEFAULT 0,
            tiempo_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tiempo_fin TIMESTAMP,
            tiempo_total_segundos INTEGER DEFAULT 0,
            modo VARCHAR(20) DEFAULT 'normal',
            fecha_quiz TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(20) DEFAULT 'completado',
            observaciones TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (materia_id) REFERENCES materias(id) ON DELETE CASCADE
        );
    """)
    
    # Tabla: estadisticas_materia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas_materia (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            materia_id INTEGER NOT NULL,
            racha_actual INTEGER DEFAULT 0,
            racha_maxima INTEGER DEFAULT 0,
            total_intentos INTEGER DEFAULT 0,
            respuestas_correctas INTEGER DEFAULT 0,
            respuestas_totales INTEGER DEFAULT 0,
            tiempo_total_segundos INTEGER DEFAULT 0,
            puntaje_maximo_facil INTEGER DEFAULT 0,
            puntaje_maximo_medio INTEGER DEFAULT 0,
            puntaje_maximo_dificil INTEGER DEFAULT 0,
            UNIQUE(usuario_id, materia_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (materia_id) REFERENCES materias(id)
        );
    """)
    
    # Tabla: estadisticas_carrera
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas_carrera (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            carrera_id INTEGER NOT NULL,
            total_intentos INTEGER DEFAULT 0,
            respuestas_correctas INTEGER DEFAULT 0,
            respuestas_totales INTEGER DEFAULT 0,
            tiempo_total_segundos INTEGER DEFAULT 0,
            UNIQUE(usuario_id, carrera_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (carrera_id) REFERENCES carreras(id)
        );
    """)
    
    # Tabla: logros
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logros (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL UNIQUE,
            descripcion TEXT,
            icono VARCHAR(50),
            categoria VARCHAR(50),
            requisito TEXT,
            puntos INTEGER DEFAULT 10,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Tabla: logros_desbloqueados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logros_desbloqueados (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            logro_id INTEGER NOT NULL,
            fecha_desbloqueado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(usuario_id, logro_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (logro_id) REFERENCES logros(id)
        );
    """)
    
    # Tabla: rankings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            materia_id INTEGER,
            tipo VARCHAR(50),
            valor INTEGER,
            posicion INTEGER,
            periodo VARCHAR(50) DEFAULT 'global',
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (materia_id) REFERENCES materias(id)
        );
    """)
    
    # Tabla: concursos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS concursos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(150) NOT NULL,
            materia_id INTEGER,
            tipo VARCHAR(50) DEFAULT 'eliminacion',
            estado VARCHAR(50) DEFAULT 'proximo',
            max_participantes INTEGER DEFAULT 32,
            ronda_actual INTEGER DEFAULT 0,
            ganador_id INTEGER,
            fecha_inicio TIMESTAMP,
            fecha_fin TIMESTAMP,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (materia_id) REFERENCES materias(id),
            FOREIGN KEY (ganador_id) REFERENCES usuarios(id)
        );
    """)
    
    # Tabla: duelos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS duelos (
            id SERIAL PRIMARY KEY,
            concurso_id INTEGER,
            usuario1_id INTEGER NOT NULL,
            usuario2_id INTEGER NOT NULL,
            ganador_id INTEGER,
            pregunta_id INTEGER,
            respuesta1 CHAR(1),
            respuesta2 CHAR(1),
            tiempo_respuesta1 INTEGER,
            tiempo_respuesta2 INTEGER,
            ronda INTEGER DEFAULT 1,
            estado VARCHAR(50) DEFAULT 'activo',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (concurso_id) REFERENCES concursos(id),
            FOREIGN KEY (usuario1_id) REFERENCES usuarios(id),
            FOREIGN KEY (usuario2_id) REFERENCES usuarios(id),
            FOREIGN KEY (ganador_id) REFERENCES usuarios(id),
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
        );
    """)
    
    # Tabla: formulas_pregunta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS formulas_pregunta (
            id SERIAL PRIMARY KEY,
            pregunta_id INTEGER NOT NULL,
            posicion INTEGER DEFAULT 0,
            formula_latex TEXT NOT NULL,
            tipo VARCHAR(50) DEFAULT 'enunciado',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pregunta_id) REFERENCES preguntas(id) ON DELETE CASCADE
        );
    """)
    
    # Tabla: sesiones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            token VARCHAR(500),
            ip_address VARCHAR(45),
            user_agent VARCHAR(255),
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_expiracion TIMESTAMP,
            activa BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );
    """)
    
    # Crear índices para mejor rendimiento
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_preguntas_materia ON preguntas(materia_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materias_carrera ON materias(carrera_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_respuestas_usuario ON respuestas(usuario_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_respuestas_pregunta ON respuestas(pregunta_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_resultados_usuario ON resultados_examenes(usuario_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_estadisticas_usuario ON estadisticas_materia(usuario_id);")
    
    print("✅ Tablas creadas correctamente")


def insertar_datos_iniciales(cursor):
    """Inserta los datos iniciales en PostgreSQL"""
    
    # Insertar carreras
    cursor.execute("""
        INSERT INTO carreras (id, nombre, descripcion, icono, color, activo)
        VALUES 
            (1, 'Ingeniería', 'Carrera de Ingeniería en Informática', '⚙️', '#667eea', TRUE),
            (2, 'Medicina', 'Carrera de Medicina General', '🏥', '#f5576c', TRUE),
            (3, 'Derecho', 'Carrera de Ciencias Jurídicas', '⚖️', '#43e97b', TRUE),
            (4, 'Administración', 'Carrera de Administración Empresarial', '📊', '#ff9a56', TRUE),
            (5, 'Psicología', 'Carrera de Psicología', '🧠', '#00f2fe', TRUE),
            (6, 'Educación', 'Carrera de Educación/Pedagogía', '🎓', '#fee140', TRUE),
            (7, 'Economía', 'Carrera de Economía', '💰', '#a8edea', TRUE),
            (8, 'Ciencias', 'Carrera de Ciencias', '🔬', '#12c2e9', TRUE),
            (131, 'Ingeniería en Sistemas', 'Ingeniería en Sistemas', '⚙️', '#667eea', TRUE),
            (134, 'Administración de Empresas', 'Administración de Empresas', '📊', '#1dd1a1', TRUE),
            (135, 'Ingeniería Civil', 'Ingeniería Civil', '🏗️', '#4ecdc4', TRUE),
            (137, 'Enfermería', 'Enfermería', '⚕️', '#ff6348', TRUE),
            (139, 'Ingeniería de Petróleos', 'Ingeniería de Petróleos', '⛽', '#ff6b6b', TRUE),
            (140, 'Contabilidad', 'Contabilidad', '📈', '#5f27cd', TRUE),
            (141, 'Ingeniería en Informática', 'Ingeniería especializada en sistemas y software', '⚙️', '#667eea', TRUE)
        ON CONFLICT DO NOTHING;
    """)
    
    # Insertar logros
    cursor.execute("""
        INSERT INTO logros (nombre, descripcion, icono, categoria, requisito, puntos, activo)
        VALUES 
            ('Principiante', 'Completar tu primer quiz', '🥇', 'inicio', 'Completar 1 quiz', 10, TRUE),
            ('En Racha', 'Tener 10 respuestas correctas consecutivas', '🔥', 'racha', '10 correctas seguidas', 25, TRUE),
            ('Racha Legendaria', 'Tener 50 respuestas correctas consecutivas', '🔥🔥', 'racha', '50 correctas seguidas', 100, TRUE),
            ('Maestro', 'Obtener 100% de éxito en una materia', '💎', 'maestria', '100% éxito en materia', 75, TRUE),
            ('Campeón', 'Ganar un torneo por eliminación', '🏆', 'concurso', 'Ganar concurso', 150, TRUE),
            ('Primer Logro', 'Desbloquear tu primer logro', '⭐', 'milestone', 'Desbloquear 1 logro', 5, TRUE),
            ('Coleccionista', 'Desbloquear 10 logros', '🎖️', 'milestone', 'Desbloquear 10 logros', 50, TRUE),
            ('Estudiante Dedicado', 'Responder 100 preguntas', '📚', 'cantidad', 'Responder 100 preguntas', 30, TRUE)
        ON CONFLICT DO NOTHING;
    """)
    
    print("✅ Datos iniciales insertados correctamente")


def main():
    """Función principal para ejecutar la migración"""
    
    config = ConfiguracionDB()
    
    print("="*70)
    print("🚀 INICIANDO MIGRACIÓN A POSTGRESQL EN RENDER")
    print("="*70)
    
    try:
        print("\n⏳ Conectando a PostgreSQL...")
        conn = config.get_connection()
        cursor = conn.cursor()
        print("✅ Conexión exitosa a PostgreSQL")
        
        # Crear tablas
        print("\n📊 Creando estructura de tablas...")
        crear_tablas_postgresql(cursor)
        
        # Insertar datos iniciales
        print("\n📥 Insertando datos iniciales...")
        insertar_datos_iniciales(cursor)
        
        # Obtener información de las tablas creadas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tablas = cursor.fetchall()
        
        print("\n📋 Tablas creadas en la base de datos:")
        for tabla in tablas:
            print(f"   ✓ {tabla[0]}")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        usuarios_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM carreras;")
        carreras_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM logros;")
        logros_count = cursor.fetchone()[0]
        
        print(f"\n📈 Datos iniciales cargados:")
        print(f"   • Usuarios: {usuarios_count}")
        print(f"   • Carreras: {carreras_count}")
        print(f"   • Logros: {logros_count}")
        
        # Commit de cambios
        conn.commit()
        
        print("\n" + "="*70)
        print("🎉 MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n✅ Tu base de datos PostgreSQL está lista para usar")
        print("\n📝 Próximos pasos:")
        print("   1. Asegúrate de que tu app.py use la nueva conexión PostgreSQL")
        print("   2. Actualiza tu archivo requirements.txt con psycopg2-binary")
        print("   3. Configura las variables de entorno en Render")
        print("   4. Redeploy tu aplicación")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
