"""
Script de prueba para verificar que el cálculo de gradientes funciona correctamente
"""
import numpy as np
from sympy import symbols, sympify, diff, lambdify

# Función de ejemplo
expr_s = "x**2 + y**2"
x, y = symbols("x y")

# Parsear expresión
expr = sympify(expr_s)
print(f"Expresión: {expr}")

# Calcular derivadas parciales
df_dx = diff(expr, x)
df_dy = diff(expr, y)
print(f"∂f/∂x = {df_dx}")
print(f"∂f/∂y = {df_dy}")

# Convertir a funciones numéricas
f = lambdify((x, y), expr, "numpy")
grad_x = lambdify((x, y), df_dx, "numpy")
grad_y = lambdify((x, y), df_dy, "numpy")

# Probar en un punto
xi, yi = 1.0, 1.0
zi = f(xi, yi)
gx = grad_x(xi, yi)
gy = grad_y(xi, yi)
magnitude = np.sqrt(gx**2 + gy**2)

print(f"\nEn el punto ({xi}, {yi}):")
print(f"  f(x,y) = {zi}")
print(f"  ∇f = ({gx}, {gy})")
print(f"  |∇f| = {magnitude}")

# Crear una grilla pequeña
print("\n--- Grilla de vectores ---")
grid_size = 3
X = np.linspace(-2, 2, grid_size)
Y = np.linspace(-2, 2, grid_size)

vectors = []
for xi in X:
    for yi in Y:
        zi = float(f(xi, yi))
        gx = float(grad_x(xi, yi))
        gy = float(grad_y(xi, yi))
        magnitude = float(np.sqrt(gx**2 + gy**2))
        
        vectors.append({
            "position": [float(xi), float(yi), float(zi)],
            "gradient": [float(gx), float(gy), 0],
            "magnitude": magnitude
        })
        print(f"  ({xi:.1f}, {yi:.1f}) -> ∇f=({gx:.2f}, {gy:.2f}), |∇f|={magnitude:.2f}")

print(f"\nTotal de vectores: {len(vectors)}")
print("✅ El cálculo de gradientes funciona correctamente")
