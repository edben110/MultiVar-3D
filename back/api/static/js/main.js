// Importar Three.js y OrbitControls desde node_modules
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Escena
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// Cámara (más cerca del origen)
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(8, 8, 8);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Controles
const controls = new OrbitControls(camera, renderer.domElement);
controls.update();
controls.enableDamping = true; // suaviza movimientos
controls.dampingFactor = 0.05;
controls.minDistance = 3; // mínimo zoom
controls.maxDistance = 30; // máximo zoom
controls.target.set(0, 0, 0); // mirar al centro
controls.update();

// Luces
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(10, 20, 10);
scene.add(directionalLight);
const ambientLight = new THREE.AmbientLight(0x404040, 0.25);
scene.add(ambientLight);
scene.add(new THREE.AxesHelper(5));

// Cuadrícula 3D
const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x444444);
scene.add(gridHelper);

// Tema
function getSystemTheme() {
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
}

function applyTheme(theme) {
    const resolved = theme === 'system' ? getSystemTheme() : theme;
    document.documentElement.setAttribute('data-theme', resolved === 'dark' ? 'dark' : 'light');
    scene.background = new THREE.Color(resolved === 'dark' ? 0x0b1020 : 0xf0f0f0);
    directionalLight.intensity = resolved === 'dark' ? 1.1 : 1.0;
    ambientLight.intensity = resolved === 'dark' ? 0.35 : 0.25;
    
    // Cambiar color de la cuadrícula según el tema
    if (gridHelper) {
        gridHelper.material.color.setHex(resolved === 'dark' ? 0x888888 : 0x444444);
        gridHelper.material.opacity = resolved === 'dark' ? 0.8 : 0.6;
        gridHelper.material.transparent = true;
        gridHelper.material.needsUpdate = true;
    }
}

// Variables para gráficos actuales
let surfaceMesh = null;
let wireframeMesh = null;
let pointsObj = null;

// Función para crear superficie como malla
function createSurfaceFromData(X, Y, Z) {
    const geometry = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];
    const colors = [];

    const zMin = Math.min(...Z.flat());
    const zMax = Math.max(...Z.flat());

    const rows = Y.length;
    const cols = X.length;

    // Vertices y colores
    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const x = X[j];
            const y = Y[i];
            const z = Z[i][j];
            vertices.push(x, y, z);
            colors.push(
                (x - X[0]) / (X[X.length - 1] - X[0]),
                (y - Y[0]) / (Y[Y.length - 1] - Y[0]),
                (z - zMin) / (zMax - zMin)
            );
        }
    }

    // Índices para formar triángulos
    for (let i = 0; i < rows - 1; i++) {
        for (let j = 0; j < cols - 1; j++) {
            const a = i * cols + j;
            const b = i * cols + j + 1;
            const c = (i + 1) * cols + j;
            const d = (i + 1) * cols + j + 1;

            indices.push(a, b, d);
            indices.push(a, d, c);
        }
    }

    geometry.setAttribute("position", new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
    geometry.setIndex(indices);
    geometry.computeVertexNormals();

    const material = new THREE.MeshStandardMaterial({
        vertexColors: true,
        side: THREE.DoubleSide,
        flatShading: false,
    });

    return new THREE.Mesh(geometry, material);
}

function createWireframeFromData(X, Y, Z) {
    const rows = Y.length;
    const cols = X.length;
    const geometry = new THREE.BufferGeometry();
    const positions = [];

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols - 1; j++) {
            const a = { x: X[j], y: Y[i], z: Z[i][j] };
            const b = { x: X[j + 1], y: Y[i], z: Z[i][j + 1] };
            positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
        }
    }
    for (let j = 0; j < cols; j++) {
        for (let i = 0; i < rows - 1; i++) {
            const a = { x: X[j], y: Y[i], z: Z[i][j] };
            const b = { x: X[j], y: Y[i + 1], z: Z[i + 1][j] };
            positions.push(a.x, a.y, a.z, b.x, b.y, b.z);
        }
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    const material = new THREE.LineBasicMaterial({ color: 0x3b82f6, linewidth: 1 });
    return new THREE.LineSegments(geometry, material);
}

function createPointsFromData(X, Y, Z) {
    const rows = Y.length;
    const cols = X.length;
    const positions = [];
    const colors = [];

    const zMin = Math.min(...Z.flat());
    const zMax = Math.max(...Z.flat());

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const x = X[j];
            const y = Y[i];
            const z = Z[i][j];
            positions.push(x, y, z);
            colors.push(
                (x - X[0]) / (X[X.length - 1] - X[0]),
                (y - Y[0]) / (Y[Y.length - 1] - Y[0]),
                (z - zMin) / (zMax - zMin)
            );
        }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    const material = new THREE.PointsMaterial({ size: 0.05, vertexColors: true });
    return new THREE.Points(geometry, material);
}

// Función que llama al endpoint Django
async function calcular() {
    const expr = document.getElementById("expr").value || "x^2+y^2";
    const op = document.getElementById("op").value;
    const resultadoDiv = document.getElementById("resultado");
    
    // Mostrar indicador de carga
    resultadoDiv.innerHTML = '<span style="color: #3b82f6;">⏳ Calculando...</span>';

    try {
        const res = await fetch(`/api/calcular/?expr=${encodeURIComponent(expr)}&op=${op}`);
        
        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        
        const data = await res.json();

        if (data.error) {
            resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ Error: ${data.error}</span>`;
            return;
        }

        if (op === "superficie") {
            // Limpiar gráficas anteriores
            if (surfaceMesh) { scene.remove(surfaceMesh); surfaceMesh.geometry.dispose(); surfaceMesh.material.dispose(); surfaceMesh = null; }
            if (wireframeMesh) { scene.remove(wireframeMesh); wireframeMesh.geometry.dispose(); wireframeMesh.material.dispose(); wireframeMesh = null; }
            if (pointsObj) { scene.remove(pointsObj); pointsObj.geometry.dispose(); pointsObj.material.dispose(); pointsObj = null; }

            // Verificar si los datos son válidos para graficar
            if (!data.x || !data.y || !data.z || data.x.length === 0 || data.y.length === 0 || data.z.length === 0) {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ Esta fórmula no es válida para graficar en 3D</span>';
                return;
            }

            // Verificar si hay valores válidos en Z
            const zValues = data.z.flat();
            const hasValidValues = zValues.some(z => !isNaN(z) && isFinite(z));
            
            if (!hasValidValues) {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ Esta fórmula no genera valores válidos para graficar</span>';
                return;
            }

            // Crear superficie por defecto
            surfaceMesh = createSurfaceFromData(data.x, data.y, data.z);
            scene.add(surfaceMesh);
            resultadoDiv.innerHTML = '<span style="color: #10b981;">✅ Superficie graficada correctamente</span>';
        } else if (op === "derivada_x") {
            if (data.derivada && data.derivada !== "Error") {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Derivada respecto a x:</span><br><code>${data.derivada}</code>`;
            } else {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ No se pudo calcular la derivada respecto a x</span>';
            }
        } else if (op === "derivada_y") {
            if (data.derivada && data.derivada !== "Error") {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Derivada respecto a y:</span><br><code>${data.derivada}</code>`;
            } else {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ No se pudo calcular la derivada respecto a y</span>';
            }
        } else if (op === "integral_doble") {
            if (data.integral && data.integral !== "Error") {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Integral doble:</span><br><code>${data.integral}</code>`;
            } else {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ No se pudo calcular la integral doble</span>';
            }
        }
    } catch (err) {
        console.error(err);
        const resultadoDiv = document.getElementById("resultado");
        
        if (err.message.includes('HTTP')) {
            resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ Error del servidor: ${err.message}</span>`;
        } else if (err.message.includes('Failed to fetch')) {
            resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ No se pudo conectar al servidor. Verifica que esté ejecutándose.</span>';
        } else {
            resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ Error: ${err.message}</span>`;
        }
    }
}

// Asociar la función al botón
document.getElementById("btnCalcular").addEventListener("click", calcular);

// Inicialización de tema y selectores
let currentTheme = localStorage.getItem('theme') || 'light';
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.querySelector('.theme-icon');

function updateThemeIcon(theme) {
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
    applyTheme(currentTheme);
    updateThemeIcon(currentTheme);
}

if (themeToggle) {
    applyTheme(currentTheme);
    updateThemeIcon(currentTheme);
    themeToggle.addEventListener('click', toggleTheme);
}

// Escuchar cambios del sistema cuando tema = system
const mq = window.matchMedia('(prefers-color-scheme: dark)');
if (mq && mq.addEventListener) {
    mq.addEventListener('change', () => {
        const current = localStorage.getItem('theme') || 'light';
        if (current === 'system') applyTheme('system');
    });
}


// Botones de ejemplo
const exampleButtons = document.querySelectorAll('.example-btn');
exampleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const expr = btn.getAttribute('data-expr');
        document.getElementById('expr').value = expr;
        calcular();
    });
});

// Graficar automáticamente al cargar la página
window.addEventListener('load', () => {
    setTimeout(() => {
        calcular();
    }, 500);
});

// Render loop
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();

// Ajustar tamaño al cambiar la ventana
window.addEventListener("resize", () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
});