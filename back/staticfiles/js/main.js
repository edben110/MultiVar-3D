import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// --- Escena, cámara, renderer, controles (igual que antes) ---
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(8, 8, 8);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.update();
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.minDistance = 3;
controls.maxDistance = 30;
controls.target.set(0, 0, 0);
controls.update();

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(10, 20, 10);
scene.add(directionalLight);
const ambientLight = new THREE.AmbientLight(0x404040, 0.25);
scene.add(ambientLight);
scene.add(new THREE.AxesHelper(5));

const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x444444);
scene.add(gridHelper);

// Theme functions (igual)
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
    if (gridHelper) {
        gridHelper.material.color.setHex(resolved === 'dark' ? 0x888888 : 0x444444);
        gridHelper.material.opacity = resolved === 'dark' ? 0.8 : 0.6;
        gridHelper.material.transparent = true;
        gridHelper.material.needsUpdate = true;
    }
}

// --- variables para objetos actuales ---
let surfaceMesh = null;
let wireframeMesh = null;
let pointsObj = null;
let gradientArrow = null;

// ==== creación de geometrías (idénticas) ====
function createSurfaceFromData(X, Y, Z) {
    const geometry = new THREE.BufferGeometry();
    const vertices = [];
    const indices = [];
    const colors = [];

    const zMin = Math.min(...Z.flat());
    const zMax = Math.max(...Z.flat());

    const rows = Y.length;
    const cols = X.length;

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            const x = X[j];
            const y = Y[i];
            const z = Z[i][j];
            vertices.push(x, y, z);
            colors.push(
                (x - X[0]) / (X[X.length - 1] - X[0] || 1),
                (y - Y[0]) / (Y[Y.length - 1] - Y[0] || 1),
                (z - zMin) / (zMax - zMin || 1)
            );
        }
    }

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
                (x - X[0]) / (X[X.length - 1] - X[0] || 1),
                (y - Y[0]) / (Y[Y.length - 1] - Y[0] || 1),
                (z - zMin) / (zMax - zMin || 1)
            );
        }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    const material = new THREE.PointsMaterial({ size: 0.05, vertexColors: true });
    return new THREE.Points(geometry, material);
}

// ==== Llamada al backend y manejo de respuestas ====
async function calcular() {
    const expr = document.getElementById("expr").value || "x^2+y^2";
    const op = document.getElementById("op").value;
    const resultadoDiv = document.getElementById("resultado");

    // Leer parámetros dinámicos
    const paramsContainer = document.getElementById('op-params');
    const inputs = paramsContainer.querySelectorAll('input, textarea');
    const searchParams = new URLSearchParams();
    searchParams.set('expr', expr);
    searchParams.set('op', op);
    inputs.forEach(inp => {
        if (inp.value !== '') searchParams.set(inp.name, inp.value);
    });

    resultadoDiv.innerHTML = '<span style="color: #3b82f6;">⏳ Calculando...</span>';

    try {
        const res = await fetch(`/api/calcular/?${searchParams.toString()}`);

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        const data = await res.json();

        if (data.error) {
            resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ Error: ${data.error}</span>`;
            return;
        }

        // Limpiar flecha previa si aplica
        if (gradientArrow) {
            scene.remove(gradientArrow);
            gradientArrow = null;
        }

        if (op === "superficie") {
            // limpiar superficies previas
            if (surfaceMesh) { scene.remove(surfaceMesh); surfaceMesh.geometry.dispose(); surfaceMesh.material.dispose(); surfaceMesh = null; }
            if (wireframeMesh) { scene.remove(wireframeMesh); wireframeMesh.geometry.dispose(); wireframeMesh.material.dispose(); wireframeMesh = null; }
            if (pointsObj) { scene.remove(pointsObj); pointsObj.geometry.dispose(); pointsObj.material.dispose(); pointsObj = null; }

            if (!data.x || !data.y || !data.z || data.x.length === 0 || data.y.length === 0 || data.z.length === 0) {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ Esta fórmula no es válida para graficar en 3D</span>';
                return;
            }
            const zValues = data.z.flat();
            const hasValidValues = zValues.some(z => !isNaN(z) && isFinite(z));
            if (!hasValidValues) {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ Esta fórmula no genera valores válidos para graficar</span>';
                return;
            }

            surfaceMesh = createSurfaceFromData(data.x, data.y, data.z);
            scene.add(surfaceMesh);
            resultadoDiv.innerHTML = '<span style="color: #10b981;">✅ Superficie graficada correctamente</span>';
        } else if (op.startsWith("derivada")) {
            if (data.derivada) {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Resultado:</span><br><code>${data.derivada}</code>`;
            } else {
                resultadoDiv.innerHTML = '<span style="color: #ef4444;">❌ No se pudo calcular la derivada</span>';
            }
        } else if (op === "integral_doble" || op === "integral_triple") {
            const key = op === "integral_doble" ? "integral" : "integral_triple";
            if (data[key]) {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ ${op === "integral_doble" ? 'Integral doble' : 'Integral triple'}:</span><br><code>${data[key]}</code>`;
            } else {
                resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ No se pudo calcular ${op}</span>`;
            }
        } else if (op === "dominio_rango") {
            const min = data.rango_min, max = data.rango_max;
            const ratio = data.dominio_valido_ratio;
            resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Dominio/Rango estimado:</span><br>
                <strong>Rango mínimo:</strong> ${min}<br>
                <strong>Rango máximo:</strong> ${max}<br>
                <strong>Proporción de puntos válidos en malla:</strong> ${(ratio*100).toFixed(2)}%`;
        } else if (op === "limite") {
            if (data.limite) {
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Límite:</span><br><code>${data.limite}</code><br>
                <small>Iterativo (x→a luego y→b): ${data.limite_iterativo_xy} — (y→b luego x→a): ${data.limite_iterativo_yx}</small>`;
            } else {
                resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ No se pudo calcular el límite</span>`;
            }
        } else if (op === "gradiente") {
            if (data.gradiente_numerico) {
                const gx = data.gradiente_numerico.x;
                const gy = data.gradiente_numerico.y;
                resultadoDiv.innerHTML = `<span style="color: #10b981;">✅ Gradiente numérico en punto:</span><br><code>(${gx.toFixed(6)}, ${gy.toFixed(6)})</code>`;
                // Dibujar flecha del gradiente en el punto (x0,y0,z0 eval)
                const x0 = parseFloat(document.querySelector('input[name="x0"]').value || 0);
                const y0 = parseFloat(document.querySelector('input[name="y0"]').value || 0);
                // Para z0 intentamos tomar valor si el usuario lo dió, sino 0
                const z0Input = document.querySelector('input[name="z0"]');
                let z0 = 0;
                if (z0Input && z0Input.value !== '') {
                    z0 = parseFloat(z0Input.value);
                } else {
                    // si hay una superficie en escena, intentar aproximar Z evaluando el mesh punto más cercano
                    z0 = 0;
                }
                // crear flecha: dirección (gx, gy, 0) y escalar para que sea visible
                const dir = new THREE.Vector3(gx, gy, 0);
                if (dir.length() === 0) {
                    // si gradiente cero, mostrar mensaje
                    resultadoDiv.innerHTML += `<br><small>Gradiente nulo (posible extremo).</small>`;
                } else {
                    dir.normalize();
                    const origin = new THREE.Vector3(x0, y0, z0);
                    const length = Math.min(3, Math.max(0.5, Math.sqrt(gx*gx + gy*gy)));
                    const hex = 0xff0000;
                    gradientArrow = new THREE.ArrowHelper(dir, origin, length, hex, 0.5*length, 0.3*length);
                    scene.add(gradientArrow);
                }
            } else {
                resultadoDiv.innerHTML = `<span style="color: #ef4444;">❌ No se pudo calcular el gradiente</span>`;
            }
        } else if (op === "lagrange") {
            if (data.lagrange_solutions) {
                if (data.lagrange_solutions.length === 0) {
                    resultadoDiv.innerHTML = `<span style="color:#ef4444;">No se encontraron soluciones reales con Lagrange.</span>`;
                } else {
                    resultadoDiv.innerHTML = `<span style="color:#10b981;">✅ Soluciones (x,y,λ):</span><br><pre>${JSON.stringify(data.lagrange_solutions, null, 2)}</pre>`;
                }
            } else {
                resultadoDiv.innerHTML = `<span style="color:#ef4444;">❌ Error en Lagrange</span>`;
            }
        } else {
            resultadoDiv.innerHTML = `<code>${JSON.stringify(data)}</code>`;
        }

    } catch (err) {
        console.error(err);
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

// Tema y botones de ejemplo (igual que antes)
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

// Cambios: inputs dinámicos según operación seleccionada
const opSelect = document.getElementById('op');
const opParams = document.getElementById('op-params');

function clearOpParams() {
    opParams.innerHTML = '';
    opParams.style.display = 'none';
}

function showOpParamsFor(op) {
    clearOpParams();
    if (op === 'limite') {
        opParams.style.display = 'block';
        opParams.innerHTML = `
            <label>Punto a (a,b)</label>
            <input name="a" placeholder="a (ej: 0)" />
            <input name="b" placeholder="b (ej: 0)" />
        `;
    } else if (op === 'gradiente') {
        opParams.style.display = 'block';
        opParams.innerHTML = `
            <label>Punto (x0,y0) y opcional z0 para dibujar flecha</label>
            <input name="x0" placeholder="x0 (ej: 1)" />
            <input name="y0" placeholder="y0 (ej: 0)" />
            <input name="z0" placeholder="z0 (ej: 0)" />
        `;
    } else if (op === 'lagrange') {
        opParams.style.display = 'block';
        opParams.innerHTML = `
            <label>Restricción g(x,y) = c</label>
            <input name="g" placeholder="g(x,y) (ej: x^2 + y^2)" />
            <input name="c" placeholder="c (ej: 1)" />
            <small>Ej: para buscar extremos con restricción x^2+y^2=1 => g="x^2+y^2" y c="1"</small>
        `;
    } else {
        // otras operaciones no requieren parámetros
        clearOpParams();
    }
}

opSelect.addEventListener('change', (e) => {
    showOpParamsFor(e.target.value);
});

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

// Ajustar tamaño
window.addEventListener("resize", () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
});
