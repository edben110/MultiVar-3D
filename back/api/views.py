from django.shortcuts import render
from django.http import JsonResponse
from sympy import (
    symbols, sympify, diff, integrate, lambdify, sin, cos, tan, sqrt, log, exp, Abs,
    limit as sym_limit, Eq, symbols as S_symbols
)
import numpy as np
import re
import json

# Variables simbólicas globales
x, y, z, lam = symbols("x y z lam")

def index(request):
    return render(request, "index.html")

def _normalize_expr(expr_str: str) -> str:
    # Reglas básicas de normalización
    s = expr_str.replace("^", "**")
    s = s.lower()
    # insertar multiplicación simple entre número y variable: 2x -> 2*x
    s = re.sub(r'(\d)(\s*)([a-zA-Z])', r'\1*\3', s)
    # entre variable y variable con espacio: x y -> x*y
    s = re.sub(r'([a-zA-Z])(\s+)([a-zA-Z])', r'\1*\3', s)
    return s

def _safe_sympify(expr_str: str):
    # Sympy puede recibir funciones matemáticas; aquí permitimos las usuales.
    # Evitamos ejecutar código peligroso dejando que sympify trabaje en modo seguro.
    return sympify(expr_str, evaluate=True)

def calcular(request):
    expr_str_raw = request.GET.get("expr", "x^2 + y^2")
    operacion = request.GET.get("op", "superficie")

    expr_str = _normalize_expr(expr_str_raw)

    # parámetros opcionales para operaciones adicionales
    # para límite: a,b ; para gradiente: x0,y0,z0 (z0 opcional)
    # para lagrange: g (restricción), c (valor)
    params = {
        "a": request.GET.get("a"),
        "b": request.GET.get("b"),
        "x0": request.GET.get("x0"),
        "y0": request.GET.get("y0"),
        "z0": request.GET.get("z0"),
        "g": request.GET.get("g"),   # restricción g(x,y)
        "c": request.GET.get("c"),   # valor constante de la restricción
    }

    # Preprocesar expresión
    try:
        expr = _safe_sympify(expr_str)
    except Exception as e:
        return JsonResponse({"error": f"Expresión inválida: {str(e)}"})

    # Verificar variables permitidas
    allowed_vars = set(['x', 'y', 'z'])
    found_vars = set(str(symbol) for symbol in expr.free_symbols)
    if found_vars and not found_vars.issubset(allowed_vars):
        invalid_vars = found_vars - allowed_vars
        return JsonResponse({"error": f"❌ Variables no permitidas: {', '.join(invalid_vars)}. Solo x,y,z."})

    resultado = {}

    try:
        if operacion in ("derivada_x", "derivada_y", "derivada_z"):
            var_map = {"derivada_x": x, "derivada_y": y, "derivada_z": z}
            dv = diff(expr, var_map[operacion])
            resultado["derivada"] = str(dv)

        elif operacion == "integral_doble":
            # integral en rectángulo [-1,1]x[-1,1] por defecto
            val = integrate(expr, (x, -1, 1), (y, -1, 1))
            resultado["integral"] = str(val)

        elif operacion == "integral_triple":
            # integral triple sobre [-1,1]^3 por defecto
            val = integrate(expr, (x, -1, 1), (y, -1, 1), (z, -1, 1))
            resultado["integral_triple"] = str(val)

        elif operacion == "superficie":
            # Igual que antes: evaluar la superficie z = f(x,y) sobre una malla
            found_vars = set(str(symbol) for symbol in expr.free_symbols)
            # si hay z en la expresión, se considera z variable: intentamos tratar expr como función de x,y
            f = lambdify((x, y), expr, ["numpy", "math"])
            X = np.linspace(-3, 3, 150)
            Y = np.linspace(-3, 3, 150)
            Z = []
            for yi in Y:
                row = []
                for xi in X:
                    try:
                        val = f(xi, yi)
                        val_float = float(val)
                        if np.isnan(val_float) or np.isinf(val_float):
                            row.append(0.0)
                        else:
                            row.append(val_float)
                    except Exception:
                        row.append(0.0)
                Z.append(row)
            resultado = {"x": list(X), "y": list(Y), "z": Z}

        elif operacion == "dominio_rango":
            # Evaluación numérica en malla para estimar dominio (puntos válidos) y rango (min/max)
            X = np.linspace(-3, 3, 101)
            Y = np.linspace(-3, 3, 101)
            valid = 0
            total = 0
            values = []
            f = lambdify((x, y), expr, ["numpy", "math"])
            for yi in Y:
                for xi in X:
                    total += 1
                    try:
                        v = f(xi, yi)
                        v = float(v)
                        if np.isfinite(v) and not np.isnan(v):
                            valid += 1
                            values.append(v)
                    except Exception:
                        # punto inválido
                        pass
            if values:
                resultado["rango_min"] = float(np.min(values))
                resultado["rango_max"] = float(np.max(values))
            else:
                resultado["rango_min"] = None
                resultado["rango_max"] = None
            resultado["dominio_valido_ratio"] = valid / total

        elif operacion == "limite":
            # parámetros a,b - punto al que tiende (x,y)->(a,b)
            a = params.get("a")
            b = params.get("b")
            if a is None or b is None:
                return JsonResponse({"error": "Para límite necesitas enviar a y b (ej: &a=0&b=0)."})
            try:
                a_val = sympify(a)
                b_val = sympify(b)
                # calcular límite iterativo: primero x->a, luego y->b, y también y->b luego x->a y comparar
                lim1 = sym_limit(sym_limit(expr, x, a_val), y, b_val)
                lim2 = sym_limit(sym_limit(expr, y, b_val), x, a_val)
                # intentar límite directo si aplica (solo si la expresión depende de x,y)
                resultado["limite_iterativo_xy"] = str(lim1)
                resultado["limite_iterativo_yx"] = str(lim2)
                if lim1 == lim2:
                    resultado["limite"] = str(lim1)
                else:
                    resultado["limite"] = f"No único / diferentes ({lim1} vs {lim2})"
            except Exception as e:
                return JsonResponse({"error": f"Error al calcular límite: {str(e)}"})

        elif operacion == "gradiente":
            # devolver gradiente simbólico y numérico en punto (x0,y0). Si se pasa z0 se incluye (pero gradiente clásico es en x,y)
            x0 = params.get("x0")
            y0 = params.get("y0")
            if x0 is None or y0 is None:
                return JsonResponse({"error": "Para gradiente necesitas enviar x0 e y0 (ej: &x0=1&y0=2)."})
            try:
                # derivadas parciales
                dfx = diff(expr, x)
                dfy = diff(expr, y)
                # evaluar numéricamente
                f_dfx = lambdify((x, y), dfx, ["numpy", "math"])
                f_dfy = lambdify((x, y), dfy, ["numpy", "math"])
                x0n = float(sympify(x0))
                y0n = float(sympify(y0))
                gx = float(f_dfx(x0n, y0n))
                gy = float(f_dfy(x0n, y0n))
                resultado["gradiente_simbolico"] = {"df/dx": str(dfx), "df/dy": str(dfy)}
                resultado["gradiente_numerico"] = {"x": gx, "y": gy}
            except Exception as e:
                return JsonResponse({"error": f"Error al calcular gradiente: {str(e)}"})

        elif operacion == "lagrange":
            # metodod de multiplicadores de Lagrange para f(x,y) con restricción g(x,y)=c
            g_expr_raw = params.get("g")
            c_raw = params.get("c")
            if not g_expr_raw or c_raw is None:
                return JsonResponse({"error": "Para Lagrange necesitas enviar g (ej: x^2+y^2) y c (ej: 1)."})
            try:
                g_expr = _safe_sympify(_normalize_expr(g_expr_raw))
                c_val = sympify(c_raw)
                # variables desconocidas: x,y
                # sistema: grad(f) - lam*grad(g) = 0 ; g(x,y) - c = 0
                dfx = diff(expr, x)
                dfy = diff(expr, y)
                dgx = diff(g_expr, x)
                dgy = diff(g_expr, y)
                # resolver simbólicamente
                # Creamos ecuaciones
                eq1 = Eq(dfx - lam * dgx, 0)
                eq2 = Eq(dfy - lam * dgy, 0)
                eq3 = Eq(g_expr - c_val, 0)
                # usar sympy.solve
                from sympy import solve
                sols = solve([eq1, eq2, eq3], [x, y, lam], dict=True)
                # convertir soluciones a lista serializable
                sol_list = []
                for s in sols:
                    sol_list.append({ 'x': str(s[x]), 'y': str(s[y]), 'lam': str(s[lam]) })
                resultado["lagrange_solutions"] = sol_list
            except Exception as e:
                return JsonResponse({"error": f"Error en Lagrange: {str(e)}"})

        else:
            return JsonResponse({"error": f"Operación desconocida: {operacion}"})
    except Exception as e:
        return JsonResponse({"error": f"Error al procesar la operación: {str(e)}"})

    return JsonResponse(resultado)
