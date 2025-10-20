#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar funciones 3D
"""

import numpy as np
from sympy import symbols, sympify, lambdify

def test_function(expr_str, xmin=-3, xmax=3, ymin=-3, ymax=3, zmin=-3, zmax=3, nx=30, ny=30, nz=30, iso_value=0):
    """Prueba una función 3D"""
    print(f"\n{'='*60}")
    print(f"Probando: {expr_str}")
    print(f"Isovalor: {iso_value}")
    print(f"{'='*60}")
    
    x, y, z = symbols("x y z")
    expr_s_sym = expr_str.replace("^", "**")
    expr = sympify(expr_s_sym)
    free_symbols = expr.free_symbols
    
    print(f"Variables detectadas: {free_symbols}")
    
    if z in free_symbols:
        print("✓ Detectada variable Z - Usando método 3D")
        
        f = lambdify((x, y, z), expr, "numpy")
        
        # Crear grilla 3D
        X = np.linspace(xmin, xmax, nx)
        Y = np.linspace(ymin, ymax, ny)
        Z = np.linspace(zmin, zmax, nz)
        
        # Evaluar en muestra y obtener rango
        all_values = []
        for i in range(0, nx, max(1, nx//10)):
            for j in range(0, ny, max(1, ny//10)):
                for k in range(0, nz, max(1, nz//10)):
                    try:
                        val = float(f(X[i], Y[j], Z[k]))
                        if np.isfinite(val):
                            all_values.append(val)
                    except:
                        continue
        
        if len(all_values) == 0:
            print("❌ ERROR: No hay valores válidos")
            return False
        
        val_min = np.min(all_values)
        val_max = np.max(all_values)
        val_range = val_max - val_min
        
        print(f"Rango de valores: [{val_min:.4f}, {val_max:.4f}]")
        print(f"Amplitud: {val_range:.4f}")
        
        # Determinar tolerancia
        if iso_value != 0:
            tolerance = max(0.2, val_range * 0.02)
        else:
            tolerance = val_range * 0.1
        
        print(f"Tolerancia: {tolerance:.4f}")
        
        # Contar puntos
        vertices = []
        
        if iso_value != 0:
            # Modo isosuperficie
            for i in range(nx):
                for j in range(ny):
                    for k in range(nz):
                        try:
                            val = float(f(X[i], Y[j], Z[k]))
                            if np.isfinite(val) and abs(val - iso_value) <= tolerance:
                                vertices.append([float(X[i]), float(Y[j]), float(Z[k])])
                        except:
                            continue
        else:
            # Modo múltiples isovalores
            num_layers = 8
            iso_levels = np.linspace(val_min + val_range*0.1, val_max - val_range*0.1, num_layers)
            
            for iso_level in iso_levels:
                tolerance_layer = val_range * 0.05
                for i in range(nx):
                    for j in range(ny):
                        for k in range(nz):
                            try:
                                val = float(f(X[i], Y[j], Z[k]))
                                if np.isfinite(val) and abs(val - iso_level) <= tolerance_layer:
                                    vertices.append([float(X[i]), float(Y[j]), float(Z[k])])
                            except:
                                continue
        
        print(f"✓ Puntos generados: {len(vertices)}")
        
        if len(vertices) > 0:
            print("✅ ÉXITO: Función graficable")
            return True
        else:
            print("❌ ERROR: No se generaron puntos")
            return False
    else:
        print("✓ Función 2D - z = f(x,y)")
        return True

# Probar las funciones problemáticas
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA DE FUNCIONES 3D")
    print("="*60)
    
    # Funciones a probar
    tests = [
        ("x^2 + y^2 + z^2", 0, True),
        ("x^2 + y^2 + z^2", 9, True),  # Esfera radio 3
        ("sqrt(x^2 + y^2 + z^2)", 0, True),
        ("x*y*z", 0, True),
        ("x^2 + y^2", 0, False),  # 2D para comparación
    ]
    
    results = []
    for expr, iso_val, expects_3d in tests:
        result = test_function(expr, iso_value=iso_val, nx=40, ny=40, nz=40)
        results.append((expr, iso_val, result))
    
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    for expr, iso_val, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {expr} (iso={iso_val}): {'ÉXITO' if result else 'FALLO'}")
