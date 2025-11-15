// ==========================================
// QUIZ SELECTOR - Seleccionar Carrera, Semestre, Materia y Modo
// ==========================================

let quizSelection = {
    carrera: null,
    semestre: null,
    materia: null,
    dificultad: null
};

let quizData = {
    carreras: [],
    semestres: [],
    materias: []
};

// ==================== INICIALIZACIÓN ====================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Quiz Selector cargado');
    await cargarCarreras();
});

// ==================== PASO 1: CARRERAS ====================
async function cargarCarreras() {
    try {
        const response = await fetch('/api/carreras');
        if (!response.ok) throw new Error('Error al cargar carreras');
        
        quizData.carreras = await response.json();
        renderCarreras();
    } catch (error) {
        console.error('Error cargando carreras:', error);
        document.getElementById('carreras-grid').innerHTML = '<p class="error">Error al cargar carreras</p>';
    }
}

function renderCarreras() {
    const grid = document.getElementById('carreras-grid');
    grid.innerHTML = '';
    
    quizData.carreras.forEach(carrera => {
        const card = document.createElement('div');
        card.className = 'carrera-card';
        card.onclick = () => seleccionarCarrera(carrera);
        card.innerHTML = `
            <div class="carrera-icon" style="background: ${carrera.color}30;">
                ${carrera.icono || '📚'}
            </div>
            <h3>${carrera.nombre}</h3>
            <p>${carrera.descripcion || ''}</p>
        `;
        grid.appendChild(card);
    });
}

function seleccionarCarrera(carrera) {
    quizSelection.carrera = carrera;
    console.log('Carrera seleccionada:', carrera.nombre);
    irPaso(2);
    cargarSemestres(carrera.id);
}

// ==================== PASO 2: SEMESTRES ====================
async function cargarSemestres(carreraId) {
    try {
        const response = await fetch(`/api/materias/carrera/${carreraId}`);
        if (!response.ok) throw new Error('Error al cargar semestres');
        
        const materias = await response.json();
        quizData.semestres = [...new Set(materias.map(m => m.semestre))].sort((a, b) => a - b);
        renderSemestres();
    } catch (error) {
        console.error('Error cargando semestres:', error);
        document.getElementById('semestres-grid').innerHTML = '<p class="error">Error al cargar semestres</p>';
    }
}

function renderSemestres() {
    const grid = document.getElementById('semestres-grid');
    grid.innerHTML = '';
    
    quizData.semestres.forEach(semestre => {
        const card = document.createElement('div');
        card.className = 'semestre-card';
        card.onclick = () => seleccionarSemestre(semestre);
        card.innerHTML = `
            <div class="semestre-number">${semestre}</div>
            <h4>Semestre ${semestre}</h4>
        `;
        grid.appendChild(card);
    });
}

function seleccionarSemestre(semestre) {
    quizSelection.semestre = semestre;
    console.log('Semestre seleccionado:', semestre);
    irPaso(3);
    cargarMaterias(quizSelection.carrera.id, semestre);
}

// ==================== PASO 3: MATERIAS ====================
async function cargarMaterias(carreraId, semestre) {
    try {
        const response = await fetch(`/api/materias/carrera/${carreraId}`);
        if (!response.ok) throw new Error('Error al cargar materias');
        
        const todasMaterias = await response.json();
        quizData.materias = todasMaterias.filter(m => m.semestre === semestre);
        renderMaterias();
    } catch (error) {
        console.error('Error cargando materias:', error);
        document.getElementById('materias-grid').innerHTML = '<p class="error">Error al cargar materias</p>';
    }
}

function renderMaterias() {
    const grid = document.getElementById('materias-grid');
    grid.innerHTML = '';
    
    if (quizData.materias.length === 0) {
        grid.innerHTML = '<p class="no-data">No hay materias en este semestre</p>';
        return;
    }
    
    quizData.materias.forEach(materia => {
        const card = document.createElement('div');
        card.className = 'materia-card';
        card.onclick = () => seleccionarMateria(materia);
        card.innerHTML = `
            <h4>${materia.nombre}</h4>
            <p>${materia.profesor || 'Sin profesor'}</p>
            <span class="preguntas-count">${materia.cantidad_preguntas || 0} preguntas</span>
        `;
        grid.appendChild(card);
    });
}

function seleccionarMateria(materia) {
    quizSelection.materia = materia;
    console.log('Materia seleccionada:', materia.nombre);
    irPaso(4);
}

// ==================== PASO 4: MODO ====================
function iniciarQuiz(dificultad) {
    quizSelection.dificultad = dificultad;
    console.log('Dificultad seleccionada:', dificultad);
    
    // Guardar selección en localStorage
    localStorage.setItem('quizSelection', JSON.stringify(quizSelection));
    
    // Redirigir a la página de quiz
    window.location.href = '/quiz';
}

// ==================== NAVEGACIÓN ====================
function irPaso(numPaso) {
    document.querySelectorAll('.selector-step').forEach(step => {
        step.classList.remove('active');
    });
    document.getElementById(`step-${numPaso}-${getPasoName(numPaso)}`).classList.add('active');
}

function volverPaso(numPaso) {
    irPaso(numPaso);
}

function getPasoName(num) {
    const names = { 1: 'carrera', 2: 'semestre', 3: 'materia', 4: 'modo' };
    return names[num];
}