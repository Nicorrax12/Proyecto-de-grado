// quiz.js - CON USUARIO_ID DEL LOGIN Y GUARDADO DE SESIONES
// Ruta: /static/js/quiz.js

let quizState = {
    selection: null,
    preguntas: [],
    indiceActual: 0,
    respuestas: [],
    puntaje: 0,
    vidas: 1,
    vidasIniciales: 1,
    tiempoInicio: null,
    timerInterval: null,
    modoActual: 'medio',
    tiempoTotal: 0,
    usuarioId: null,
    materiaId: null
};

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎯 === INICIALIZANDO QUIZ ===');
    
    // Obtener parámetros de URL
    const params = new URLSearchParams(window.location.search);
    const materiaId = params.get('materia_id');
    const modo = params.get('modo') || 'medio';
    
    // Obtener usuario del localStorage (del login)
    const usuarioStr = localStorage.getItem('usuarioActual');
    if (usuarioStr) {
        const usuario = JSON.parse(usuarioStr);
        quizState.usuarioId = usuario.id;
        console.log(`✅ Usuario logueado: ${usuario.nombre} (ID: ${usuario.id})`);
    } else {
        console.warn('⚠️ Sin usuario logueado, pero continuando...');
    }
    
    console.log('📊 Parámetros de URL:', { materiaId, modo, usuarioId: quizState.usuarioId });
    
    // Configurar vidas según modo
    const vidasPorModo = {
        'facil': 1,      // Normal: 1 vida
        'medio': 3,      // Hardcore: 3 vidas
        'dificil': 1     // Pesadilla: 1 vida
    };
    
    quizState.modoActual = modo;
    quizState.vidasIniciales = vidasPorModo[modo] || 1;
    quizState.vidas = quizState.vidasIniciales;
    quizState.materiaId = parseInt(materiaId);
    
    console.log(`🎮 Modo: ${modo} | Vidas: ${quizState.vidas} | Materia: ${materiaId}`);
    
    // Recuperar datos del localStorage
    const selectionStr = localStorage.getItem('quizSelection');
    if (selectionStr) {
        quizState.selection = JSON.parse(selectionStr);
        console.log('✅ Selección recuperada:', quizState.selection);
    }
    
    // Validar materia_id
    if (!materiaId || materiaId === 'null' || materiaId === '') {
        console.error('❌ materia_id inválido:', materiaId);
        mostrarError('ID de materia no válido.');
        return;
    }
    
    const materiaIdInt = parseInt(materiaId);
    if (isNaN(materiaIdInt)) {
        console.error('❌ materia_id no es un número:', materiaId);
        mostrarError('ID de materia no es válido.');
        return;
    }
    
    // Actualizar título
    if (quizState.selection && quizState.selection.materiaInfo) {
        document.getElementById('materia-titulo').textContent = quizState.selection.materiaInfo.nombre;
        document.title = `Quiz - ${quizState.selection.materiaInfo.nombre}`;
    }
    
    // Cargar preguntas
    console.log('📚 Cargando preguntas...');
    await cargarPreguntas(materiaIdInt, modo);
    
    // Si hay preguntas, mostrar la primera
    if (quizState.preguntas && quizState.preguntas.length > 0) {
        console.log('✅ Preguntas cargadas. Mostrando primera...');
        mostrarPregunta();
        iniciarTimer();
        actualizarVidas();
    } else {
        console.error('❌ No hay preguntas disponibles');
        mostrarError('No hay preguntas disponibles.');
    }
});

// ==================== CARGAR PREGUNTAS ====================
async function cargarPreguntas(materiaId, modo) {
    try {
        console.log(`📍 Cargando: materia=${materiaId}, modo=${modo}`);
        
        const url = `/api/quiz/preguntas/${materiaId}?dificultad=medio&cantidad=10`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data || data.length === 0) {
            mostrarError('No hay preguntas disponibles.');
            return;
        }
        
        quizState.preguntas = data;
        console.log(`✅ ${data.length} preguntas cargadas`);
        
        // Aleatorizar
        quizState.preguntas = quizState.preguntas.sort(() => Math.random() - 0.5);
        
        document.getElementById('total-preguntas').textContent = data.length;
        
    } catch (error) {
        console.error('❌ Error:', error);
        mostrarError(`Error al cargar preguntas: ${error.message}`);
    }
}

// ==================== MOSTRAR PREGUNTA ====================
function mostrarPregunta() {
    if (!quizState.preguntas || quizState.preguntas.length === 0) {
        return;
    }
    
    const pregunta = quizState.preguntas[quizState.indiceActual];
    
    if (!pregunta) {
        finalizarQuiz();
        return;
    }
    
    console.log(`📝 Pregunta ${quizState.indiceActual + 1}/${quizState.preguntas.length}`);
    
    document.getElementById('pregunta-actual').textContent = quizState.indiceActual + 1;
    document.getElementById('pregunta-texto').innerHTML = pregunta.texto;
    
    ['a', 'b', 'c', 'd'].forEach(opt => {
        const el = document.getElementById(`opcion-${opt}`);
        if (el) el.innerHTML = pregunta.opciones[opt] || '';
    });
    
    document.querySelectorAll('.opcion').forEach(btn => {
        btn.classList.remove('selected', 'correcta', 'incorrecta', 'disabled');
        btn.disabled = false;
    });
    
    const btnSiguiente = document.getElementById('btn-siguiente');
    if (btnSiguiente) btnSiguiente.disabled = true;
    
    if (window.MathJax) {
        MathJax.typesetPromise().catch(err => console.log('MathJax:', err));
    }
}

// ==================== SELECCIONAR OPCIÓN ====================
function seleccionarOpcion(boton) {
    const pregunta = quizState.preguntas[quizState.indiceActual];
    const opcionSeleccionada = boton.dataset.opcion;
    
    document.querySelectorAll('.opcion').forEach(btn => {
        btn.disabled = true;
        btn.classList.add('disabled');
    });
    
    const esCorrecta = opcionSeleccionada === pregunta.respuesta_correcta;
    
    if (esCorrecta) {
        console.log('✅ Correcto');
        boton.classList.add('correcta');
        quizState.puntaje++;
        document.getElementById('puntaje-actual').textContent = quizState.puntaje;
    } else {
        console.log('❌ Incorrecto');
        boton.classList.add('incorrecta');
        quizState.vidas--;
        actualizarVidas();
        
        const btnCorrecto = document.querySelector(`[data-opcion="${pregunta.respuesta_correcta}"]`);
        if (btnCorrecto) btnCorrecto.classList.add('correcta');
        
        if (quizState.vidas <= 0) {
            console.log('💀 Game Over');
            setTimeout(() => finalizarQuiz(true), 2000);
            return;
        }
    }
    
    quizState.respuestas.push({
        pregunta_id: pregunta.id,
        respuesta_dada: opcionSeleccionada,
        correcta: esCorrecta
    });
    
    const btnSiguiente = document.getElementById('btn-siguiente');
    if (btnSiguiente) btnSiguiente.disabled = false;
}

// ==================== ACTUALIZAR VIDAS ====================
function actualizarVidas() {
    const vidasElement = document.getElementById('vidas-actual');
    if (vidasElement) {
        let html = '';
        for (let i = 0; i < quizState.vidasIniciales; i++) {
            html += i < quizState.vidas ? '❤️' : '🖤';
        }
        vidasElement.innerHTML = html;
        
        if (quizState.vidas === 1) {
            vidasElement.style.color = '#ef4444';
        } else if (quizState.vidas === 2) {
            vidasElement.style.color = '#f97316';
        } else {
            vidasElement.style.color = '#10b981';
        }
    }
}

// ==================== SIGUIENTE PREGUNTA ====================
function siguientePregunta() {
    quizState.indiceActual++;
    if (quizState.indiceActual >= quizState.preguntas.length) {
        finalizarQuiz();
    } else {
        mostrarPregunta();
    }
}

// ==================== FINALIZAR QUIZ ====================
async function finalizarQuiz(gameOver = false) {
    console.log('🏁 Finalizando quiz');
    
    clearInterval(quizState.timerInterval);
    
    const totalPreguntas = quizState.preguntas.length;
    const porcentaje = ((quizState.puntaje / totalPreguntas) * 100).toFixed(1);
    const tiempoTotal = document.getElementById('tiempo-total')?.textContent || '00:00';
    
    const tiempoPartes = tiempoTotal.split(':');
    const tiempoSegundos = parseInt(tiempoPartes[0]) * 60 + parseInt(tiempoPartes[1]);
    
    console.log(`📊 Resultado: ${quizState.puntaje}/${totalPreguntas} (${porcentaje}%)`);
    
    // Guardar sesión
    if (quizState.usuarioId && quizState.materiaId) {
        console.log('💾 Guardando sesión...');
        await guardarSesion(tiempoSegundos, totalPreguntas);
    } else {
        console.warn('⚠️ Sin usuario o materia, no se guarda sesión');
    }
    
    // Mostrar resultados
    const quizContainer = document.getElementById('quiz-container');
    if (quizContainer) quizContainer.style.display = 'none';
    
    const resultadosScreen = document.getElementById('resultados-screen');
    if (resultadosScreen) {
        resultadosScreen.style.display = 'flex';
        
        if (gameOver) {
            document.getElementById('resultado-titulo').innerHTML = '💀 Game Over';
        }
        
        document.getElementById('resultado-puntaje').textContent = `${quizState.puntaje}/${totalPreguntas}`;
        document.getElementById('resultado-porcentaje').textContent = `${porcentaje}%`;
        document.getElementById('resultado-tiempo').textContent = tiempoTotal;
    }
}

// ==================== GUARDAR SESIÓN ====================
async function guardarSesion(tiempoSegundos, totalPreguntas) {
    try {
        const datos = {
            usuario_id: quizState.usuarioId,
            materia_id: quizState.materiaId,
            modo: quizState.modoActual,
            puntaje_total: quizState.puntaje,
            total_preguntas: totalPreguntas,
            preguntas_correctas: quizState.puntaje,
            tiempo_segundos: tiempoSegundos,
            vidas_restantes: quizState.vidas
        };
        
        console.log('📤 Enviando:', datos);
        
        const response = await fetch('/api/quiz/guardar-sesion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Sesión guardada:', result);
            
            const rachaEl = document.getElementById('resultado-racha');
            if (rachaEl && result.racha_actual) {
                rachaEl.textContent = `🔥 Racha Actual: ${result.racha_actual} | Racha Máxima: ${result.racha_maxima}`;
            }
        } else {
            console.error('❌ Error:', response.statusText);
        }
    } catch (error) {
        console.error('❌ Error:', error);
    }
}

// ==================== TIMER ====================
function iniciarTimer() {
    quizState.tiempoInicio = Date.now();
    quizState.timerInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - quizState.tiempoInicio) / 1000);
        const minutos = Math.floor(elapsed / 60);
        const segundos = elapsed % 60;
        
        const timerElement = document.getElementById('tiempo-total');
        if (timerElement) {
            timerElement.textContent = 
                `${String(minutos).padStart(2, '0')}:${String(segundos).padStart(2, '0')}`;
        }
    }, 1000);
}

// ==================== MOSTRAR ERROR ====================
function mostrarError(mensaje) {
    console.error('❌', mensaje);
    const quizContainer = document.getElementById('quiz-container');
    if (quizContainer) {
        quizContainer.innerHTML = `
            <div style="padding: 40px; text-align: center; background: #1e293b; border-radius: 12px; border: 2px solid #dc2626; max-width: 600px; margin: 50px auto;">
                <h2 style="color: #ef4444; margin-bottom: 15px;">❌ Error</h2>
                <p style="color: #cbd5e1; margin-bottom: 20px;">${mensaje}</p>
                <a href="/" style="display: inline-block; padding: 12px 24px; background: #667eea; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
                    Volver
                </a>
            </div>
        `;
    }
}

// ==================== ACCIONES ====================
function salirQuiz() {
    if (confirm('¿Seguro que deseas salir?')) {
        window.location.href = '/';
    }
}

function volverHome() {
    localStorage.removeItem('quizSelection');
    window.location.href = '/';
}

function nuevoQuiz() {
    localStorage.removeItem('quizSelection');
    window.location.href = '/';
}