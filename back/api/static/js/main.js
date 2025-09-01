// Importar Three.js y OrbitControls desde node_modules
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Escena
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

// Cámara (más cerca del origen)
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(10, 10, 10);

// Renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Controles
const controls = new OrbitControls(camera, renderer.domElement);
controls.update();
controls.enableDamping = true; // suaviza movimientos
controls.dampingFactor = 0.05;
controls.minDistance = 2; // mínimo zoom
controls.maxDistance = 50; // máximo zoom
controls.target.set(0, 0, 0); // mirar al centro
controls.update();

// Luces
const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(10, 20, 10);
scene.add(directionalLight);
scene.add(new THREE.AmbientLight(0x404040));
scene.add(new THREE.AxesHelper(5));

// Variable para la superficie actual
let surfaceMesh = null;

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

// Función que llama al endpoint Django
async function calcular() {
    const expr = document.getElementById("expr").value || "x^2+y^2";
    const op = document.getElementById("op").value;

    try {
        const res = await fetch(`/api/calcular/?expr=${encodeURIComponent(expr)}&op=${op}`);
        const data = await res.json();
        const resultadoDiv = document.getElementById("resultado");

        if (data.error) {
            resultadoDiv.textContent = "Error: " + data.error;
            return;
        }

        if (op === "superficie") {
            if (surfaceMesh) scene.remove(surfaceMesh);
            surfaceMesh = createSurfaceFromData(data.x, data.y, data.z);
            scene.add(surfaceMesh);
            resultadoDiv.textContent = "";
        } else if (op === "derivada_x") {
            resultadoDiv.textContent = "Derivada respecto a x: " + data.derivada;
        } else if (op === "derivada_y") {
            resultadoDiv.textContent = "Derivada respecto a y: " + data.derivada;
        } else if (op === "integral_doble") {
            resultadoDiv.textContent = "Integral doble: " + data.integral;
        }
    } catch (err) {
        console.error(err);
    }
}

// Asociar la función al botón
document.getElementById("btnCalcular").addEventListener("click", calcular);

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
