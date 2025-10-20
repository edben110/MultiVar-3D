import os
import numpy as np
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sympy import symbols, sympify, lambdify

# AppID de Wolfram Alpha
WOLFRAM_APPID = os.environ.get("WOLFRAM_APPID", "4JAEAEG4K4")

def wolfram_query(input_text: str):
    if not WOLFRAM_APPID:
        return {"error": "No WOLFRAM_APPID configurado"}

    url = "https://api.wolframalpha.com/v2/query"
    params = {
        "appid": WOLFRAM_APPID,
        "input": input_text,
        "output": "JSON",
        "format": "plaintext"
    }

    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        return {"error": "Tiempo de espera agotado al consultar Wolfram"}
    except Exception as e:
        return {"error": f"Fallo en solicitud: {str(e)}"}

    pods = data.get("queryresult", {}).get("pods", [])
    if not pods:
        return {"error": "Sin resultados de Wolfram"}

    claves_validas = [
        "result", "results", "solution", "solutions",
        "definite integral", "indefinite integral",
        "derivative", "limit", "gradient", "domain", "range",
        "global maxima", "global minima", "extrema", "critical points",
        "maximize", "minimize", "maximum", "minimum"
    ]

    for pod in pods:
        titulo = pod.get("title", "").lower()
        if any(k in titulo for k in claves_validas):
            subpods = pod.get("subpods", [])
            if subpods and "plaintext" in subpods[0]:
                texto = subpods[0]["plaintext"]
                if texto:
                    return {"resultado": texto.strip()}

    primer_subpod = pods[0].get("subpods", [])
    if primer_subpod and "plaintext" in primer_subpod[0]:
        return {"resultado": primer_subpod[0]["plaintext"].strip()}

    return {"resultado": "Sin resultado claro"}


@csrf_exempt
def calcular(request):
    expr_s = request.GET.get("expr", "x^2 + y^2")
    op = request.GET.get("op", "superficie")
    expr_s_sym = expr_s.replace("^", "**")
    x, y, z = symbols("x y z")

    try:
        # --- SUPERFICIE LOCAL ---
        if op == "superficie":
            xmin = float(request.GET.get("xmin", -3))
            xmax = float(request.GET.get("xmax", 3))
            ymin = float(request.GET.get("ymin", -3))
            ymax = float(request.GET.get("ymax", 3))
            zmin = float(request.GET.get("zmin", -3))
            zmax = float(request.GET.get("zmax", 3))
            nx = int(request.GET.get("nx", 50))
            ny = int(request.GET.get("ny", 50))
            nz = int(request.GET.get("nz", 50))
            iso_value = float(request.GET.get("iso_value", 0))

            expr = sympify(expr_s_sym)
            free_symbols = expr.free_symbols
            
            # Detectar si la expresión incluye z
            if z in free_symbols:
                # Método volumétrico para superficies 3D con z
                f = lambdify((x, y, z), expr, "numpy")
                
                # Crear grilla 3D
                X = np.linspace(xmin, xmax, nx)
                Y = np.linspace(ymin, ymax, ny)
                Z = np.linspace(zmin, zmax, nz)
                
                # Crear volumen 3D con valores de función
                volume = np.zeros((nx, ny, nz))
                for i in range(nx):
                    for j in range(ny):
                        for k in range(nz):
                            try:
                                volume[i, j, k] = float(f(X[i], Y[j], Z[k]))
                            except:
                                volume[i, j, k] = np.nan
                
                # Calcular rango de valores válidos
                valid_values = volume[np.isfinite(volume)]
                if len(valid_values) == 0:
                    return JsonResponse({"error": "La función no genera valores válidos en el rango especificado"})
                
                val_min = np.min(valid_values)
                val_max = np.max(valid_values)
                val_range = val_max - val_min
                
                # Determinar isovalor objetivo
                if iso_value == 0 and val_min * val_max < 0:
                    # Si el rango cruza cero, usar cero como isovalor
                    target_iso = 0.0
                elif iso_value == 0:
                    # Si no cruza cero, usar el valor medio
                    target_iso = (val_min + val_max) / 2
                else:
                    target_iso = iso_value
                
                # Generar malla usando marching cubes simplificado
                vertices = []
                faces = []
                vertex_map = {}
                vertex_count = 0
                
                # Función para obtener o crear vértice interpolado
                def get_vertex(i1, j1, k1, i2, j2, k2, val1, val2):
                    nonlocal vertex_count
                    
                    # Crear clave única para este edge
                    key = tuple(sorted([(i1, j1, k1), (i2, j2, k2)]))
                    
                    if key in vertex_map:
                        return vertex_map[key]
                    
                    # Interpolar posición
                    if abs(val1 - val2) < 1e-10:
                        t = 0.5
                    else:
                        t = (target_iso - val1) / (val2 - val1)
                    t = np.clip(t, 0, 1)
                    
                    x_interp = X[i1] + t * (X[i2] - X[i1])
                    y_interp = Y[j1] + t * (Y[j2] - Y[j1])
                    z_interp = Z[k1] + t * (Z[k2] - Z[k1])
                    
                    vertices.append([float(x_interp), float(y_interp), float(z_interp)])
                    vertex_map[key] = vertex_count
                    vertex_count += 1
                    
                    return vertex_map[key]
                
                # Procesar cada cubo en la grilla
                for i in range(nx - 1):
                    for j in range(ny - 1):
                        for k in range(nz - 1):
                            # Obtener los 8 vértices del cubo
                            v = [
                                volume[i, j, k],
                                volume[i+1, j, k],
                                volume[i+1, j+1, k],
                                volume[i, j+1, k],
                                volume[i, j, k+1],
                                volume[i+1, j, k+1],
                                volume[i+1, j+1, k+1],
                                volume[i, j+1, k+1]
                            ]
                            
                            # Verificar validez
                            if not all(np.isfinite(val) for val in v):
                                continue
                            
                            # Crear código de configuración
                            cube_index = 0
                            for idx, val in enumerate(v):
                                if val >= target_iso:
                                    cube_index |= (1 << idx)
                            
                            # Si todos dentro o todos fuera, saltar
                            if cube_index == 0 or cube_index == 255:
                                continue
                            
                            # Definir las 12 aristas del cubo
                            # Formato: (vértice1, vértice2, índices_grid1, índices_grid2)
                            edges = [
                                (0, 1, (i,j,k), (i+1,j,k)),
                                (1, 2, (i+1,j,k), (i+1,j+1,k)),
                                (2, 3, (i+1,j+1,k), (i,j+1,k)),
                                (3, 0, (i,j+1,k), (i,j,k)),
                                (4, 5, (i,j,k+1), (i+1,j,k+1)),
                                (5, 6, (i+1,j,k+1), (i+1,j+1,k+1)),
                                (6, 7, (i+1,j+1,k+1), (i,j+1,k+1)),
                                (7, 4, (i,j+1,k+1), (i,j,k+1)),
                                (0, 4, (i,j,k), (i,j,k+1)),
                                (1, 5, (i+1,j,k), (i+1,j,k+1)),
                                (2, 6, (i+1,j+1,k), (i+1,j+1,k+1)),
                                (3, 7, (i,j+1,k), (i,j+1,k+1))
                            ]
                            
                            # Encontrar aristas que cruzan la isosuperficie
                            edge_vertices = []
                            for v1, v2, g1, g2 in edges:
                                val1, val2 = v[v1], v[v2]
                                # Cruza si tienen signos diferentes respecto al iso
                                if (val1 < target_iso) != (val2 < target_iso):
                                    vert_idx = get_vertex(g1[0], g1[1], g1[2], 
                                                         g2[0], g2[1], g2[2],
                                                         val1, val2)
                                    edge_vertices.append(vert_idx)
                            
                            # Crear triángulos a partir de los vértices de arista
                            # Usamos triangulación de abanico simple
                            if len(edge_vertices) >= 3:
                                # Centro promedio
                                for t in range(len(edge_vertices) - 2):
                                    faces.append([
                                        edge_vertices[0],
                                        edge_vertices[t+1],
                                        edge_vertices[t+2]
                                    ])
                
                if len(vertices) == 0 or len(faces) == 0:
                    return JsonResponse({"error": "No se pudo generar malla para esta función. Intenta ajustar el isovalor o los rangos."})
                
                return JsonResponse({
                    "type": "implicit_mesh",
                    "vertices": vertices,
                    "faces": faces,
                    "iso_value": float(target_iso),
                    "value_range": [float(val_min), float(val_max)]
                })
            else:
                # Método clásico z = f(x,y)
                f = lambdify((x, y), expr, "numpy")
                
                X = np.linspace(xmin, xmax, nx)
                Y = np.linspace(ymin, ymax, ny)
                XX, YY = np.meshgrid(X, Y)
                with np.errstate(all="ignore"):
                    ZZ = f(XX, YY)
                ZZ = np.where(np.isfinite(ZZ), ZZ, np.nan)

                return JsonResponse({
                    "type": "explicit",
                    "x": X.tolist(),
                    "y": Y.tolist(),
                    "z": ZZ.tolist()
                })

        # --- CAMPO DE GRADIENTES ---
        elif op == "campo_gradiente":
            from sympy import diff
            
            xmin = float(request.GET.get("xmin", -3))
            xmax = float(request.GET.get("xmax", 3))
            ymin = float(request.GET.get("ymin", -3))
            ymax = float(request.GET.get("ymax", 3))
            grid_size = int(request.GET.get("grid_size", 10))  # Número de flechas por eje
            
            expr = sympify(expr_s_sym)
            
            # Calcular derivadas parciales simbólicamente
            df_dx = diff(expr, x)
            df_dy = diff(expr, y)
            
            # Convertir a funciones numéricas
            f = lambdify((x, y), expr, "numpy")
            grad_x = lambdify((x, y), df_dx, "numpy")
            grad_y = lambdify((x, y), df_dy, "numpy")
            
            # Crear grilla de puntos
            X = np.linspace(xmin, xmax, grid_size)
            Y = np.linspace(ymin, ymax, grid_size)
            
            # Calcular gradiente en cada punto
            vectors = []
            for xi in X:
                for yi in Y:
                    try:
                        # Evaluar función en el punto
                        zi = float(f(xi, yi))
                        # Evaluar gradiente
                        gx = float(grad_x(xi, yi))
                        gy = float(grad_y(xi, yi))
                        
                        # Verificar que sean valores válidos
                        if np.isfinite([xi, yi, zi, gx, gy]).all():
                            vectors.append({
                                "position": [float(xi), float(yi), float(zi)],
                                "gradient": [float(gx), float(gy), 0],  # gz=0 para z=f(x,y)
                                "magnitude": float(np.sqrt(gx**2 + gy**2))
                            })
                    except:
                        continue
            
            return JsonResponse({
                "type": "gradient_field",
                "vectors": vectors,
                "expression": expr_s
            })

        # --- OPERACIONES CON WOLFRAM ---
        elif op == "derivada_x":
            query = f"derivative of {expr_s} with respect to x"
        elif op == "derivada_y":
            query = f"derivative of {expr_s} with respect to y"
        elif op == "derivada_z":
            query = f"derivative of {expr_s} with respect to z"
        elif op == "integral_doble":
            query = f"second degree integral of {expr_s} dx dy"
        elif op == "limite":
            a = request.GET.get("a", "0")
            b = request.GET.get("b", "0")
            query = f"limit of {expr_s} as x->{a} and y->{b}"
        elif op == "dominio_rango":
            # Usar formato más efectivo para Wolfram
            query = f"domain and range of {expr_s}"
        elif op == "lagrange":
            g = request.GET.get("g")
            c = request.GET.get("c")
            if not g or not c:
                return JsonResponse({"error": "g y c requeridos para Lagrange"})
            # Formato correcto para Wolfram: maximize/minimize con constraint
            # Intentar ambos (máximo y mínimo)
            query = f"extrema of {expr_s} subject to {g} = {c}"
        else:
            return JsonResponse({"error": "Operación no reconocida"}, status=400)

        # --- CONSULTA A WOLFRAM ---
        resultado = wolfram_query(query)

        if "error" in resultado:
            return JsonResponse({"error": resultado["error"]})

        valor = resultado.get("resultado", "Sin resultado")

        # --- RESPUESTAS ESTANDARIZADAS ---
        if op in ["derivada_x", "derivada_y","derivada_z"]:
            return JsonResponse({"derivada": valor})
        elif op == "integral_doble":
            return JsonResponse({"integral": valor})
        elif op == "limite":
            return JsonResponse({"limite": valor})
        elif op == "dominio_rango":
            return JsonResponse({"dominio_rango": valor})
        elif op == "lagrange":
            return JsonResponse({"lagrange": valor})
        else:
            return JsonResponse({"resultado": valor})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
