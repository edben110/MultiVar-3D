#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para marching cubes
"""

import numpy as np
from sympy import symbols, sympify, lambdify

def test_marching_cubes(expr_str, iso_value=0, nx=20, ny=20, nz=20):
    """Prueba marching cubes simplificado"""
    print(f"\n{'='*60}")
    print(f"Probando: {expr_str}")
    print(f"Isovalor: {iso_value}")
    print(f"Resolución: {nx}x{ny}x{nz}")
    print(f"{'='*60}")
    
    x, y, z = symbols("x y z")
    expr_s_sym = expr_str.replace("^", "**")
    expr = sympify(expr_s_sym)
    
    f = lambdify((x, y, z), expr, "numpy")
    
    # Crear grilla 3D
    xmin, xmax = -3, 3
    ymin, ymax = -3, 3
    zmin, zmax = -3, 3
    
    X = np.linspace(xmin, xmax, nx)
    Y = np.linspace(ymin, ymax, ny)
    Z = np.linspace(zmin, zmax, nz)
    
    # Crear volumen 3D
    volume = np.zeros((nx, ny, nz))
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                try:
                    volume[i, j, k] = float(f(X[i], Y[j], Z[k]))
                except:
                    volume[i, j, k] = np.nan
    
    # Calcular rango
    valid_values = volume[np.isfinite(volume)]
    if len(valid_values) == 0:
        print("❌ ERROR: No hay valores válidos")
        return False
    
    val_min = np.min(valid_values)
    val_max = np.max(valid_values)
    val_range = val_max - val_min
    
    print(f"Rango de valores: [{val_min:.4f}, {val_max:.4f}]")
    
    # Determinar isovalor objetivo
    if iso_value == 0 and val_min * val_max < 0:
        target_iso = 0.0
    elif iso_value == 0:
        target_iso = (val_min + val_max) / 2
    else:
        target_iso = iso_value
    
    print(f"Isovalor objetivo: {target_iso:.4f}")
    
    # Contar cubos que cruzan la isosuperficie
    crossing_cubes = 0
    vertices = []
    faces = []
    vertex_map = {}
    vertex_count = 0
    
    def get_vertex(p1, p2, val1, val2):
        nonlocal vertex_count
        if val1 == val2:
            t = 0.5
        else:
            t = (target_iso - val1) / (val2 - val1)
        t = np.clip(t, 0, 1)
        
        x_interp = p1[0] + t * (p2[0] - p1[0])
        y_interp = p1[1] + t * (p2[1] - p1[1])
        z_interp = p1[2] + t * (p2[2] - p1[2])
        
        key = f"{p1[0]:.4f},{p1[1]:.4f},{p1[2]:.4f}-{p2[0]:.4f},{p2[1]:.4f},{p2[2]:.4f}"
        
        if key not in vertex_map:
            vertices.append([float(x_interp), float(y_interp), float(z_interp)])
            vertex_map[key] = vertex_count
            vertex_count += 1
        
        return vertex_map[key]
    
    # Marching cubes simplificado
    for i in range(nx - 1):
        for j in range(ny - 1):
            for k in range(nz - 1):
                # Obtener los 8 vértices del cubo
                cube_values = [
                    volume[i, j, k],
                    volume[i+1, j, k],
                    volume[i+1, j+1, k],
                    volume[i, j+1, k],
                    volume[i, j, k+1],
                    volume[i+1, j, k+1],
                    volume[i+1, j+1, k+1],
                    volume[i, j+1, k+1]
                ]
                
                if not all(np.isfinite(v) for v in cube_values):
                    continue
                
                # Crear código de configuración
                cube_index = 0
                for idx, val in enumerate(cube_values):
                    if val >= target_iso:
                        cube_index |= (1 << idx)
                
                # Si todos dentro o todos fuera, saltar
                if cube_index == 0 or cube_index == 255:
                    continue
                
                crossing_cubes += 1
                
                # Posiciones de los vértices del cubo
                cube_positions = [
                    [X[i], Y[j], Z[k]],
                    [X[i+1], Y[j], Z[k]],
                    [X[i+1], Y[j+1], Z[k]],
                    [X[i], Y[j+1], Z[k]],
                    [X[i], Y[j], Z[k+1]],
                    [X[i+1], Y[j], Z[k+1]],
                    [X[i+1], Y[j+1], Z[k+1]],
                    [X[i], Y[j+1], Z[k+1]]
                ]
                
                # Crear triángulos simplificados
                if bin(cube_index).count('1') in [1, 7]:
                    edges = [
                        (0,1), (1,2), (2,3), (3,0),
                        (4,5), (5,6), (6,7), (7,4),
                        (0,4), (1,5), (2,6), (3,7)
                    ]
                    
                    edge_vertices = []
                    for e1, e2 in edges:
                        if (cube_values[e1] < target_iso) != (cube_values[e2] < target_iso):
                            v_idx = get_vertex(cube_positions[e1], cube_positions[e2], 
                                              cube_values[e1], cube_values[e2])
                            edge_vertices.append(v_idx)
                    
                    if len(edge_vertices) >= 3:
                        for idx in range(1, len(edge_vertices) - 1):
                            faces.append([edge_vertices[0], edge_vertices[idx], edge_vertices[idx+1]])
    
    print(f"Cubos que cruzan isosuperficie: {crossing_cubes}")
    print(f"✓ Vértices generados: {len(vertices)}")
    print(f"✓ Caras generadas: {len(faces)}")
    
    if len(vertices) > 0 and len(faces) > 0:
        print("✅ ÉXITO: Malla generada correctamente")
        return True
    else:
        print("❌ ERROR: No se generó malla")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBA DE MARCHING CUBES")
    print("="*60)
    
    tests = [
        ("x^2 + y^2 + z^2", 9, 20),    # Esfera
        ("x^2 + y^2 + z^2", 0, 20),    # Múltiples esferas
        ("x*y*z", 0, 20),               # Hiperboloide
        ("sqrt(x^2 + y^2 + z^2)", 0, 20),  # Cono
    ]
    
    results = []
    for expr, iso_val, res in tests:
        result = test_marching_cubes(expr, iso_value=iso_val, nx=res, ny=res, nz=res)
        results.append((expr, iso_val, result))
    
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    for expr, iso_val, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {expr} (iso={iso_val}): {'ÉXITO' if result else 'FALLO'}")
