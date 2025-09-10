from django.shortcuts import render
from django.http import JsonResponse
from sympy import symbols, sympify, diff, integrate, lambdify, sin, cos, tan, sqrt, log, exp, Abs
import numpy as np
import re

def index(request):
    return render(request, "index.html")

def calcular(request):
    expr_str = request.GET.get("expr", "x^2 + y^2")
    operacion = request.GET.get("op", "superficie")

    # Normalizar expresión para Sympy - enfoque simplificado
    expr_str = expr_str.replace("^", "**")
    
    # Convertir a minúsculas
    expr_str = expr_str.lower()
    
    # Solo insertar multiplicaciones implícitas básicas
    expr_str = re.sub(r'(\d)(\s*)([a-zA-Z])', r'\1*\3', expr_str)
    expr_str = re.sub(r'([a-zA-Z])(\s+)([a-zA-Z])', r'\1*\3', expr_str)
    
    # NO aplicar multiplicación implícita entre letras consecutivas
    # Dejar que SymPy maneje las funciones directamente

    x, y = symbols("x y")
    
    # Debug: imprimir la expresión procesada
    print(f"Expresión original: {request.GET.get('expr', 'x^2 + y^2')}")
    print(f"Expresión procesada: {expr_str}")
    
    try:
        expr = sympify(expr_str)
        
        # Verificar que solo contenga variables x e y usando SymPy
        allowed_vars = set(['x', 'y'])
        found_vars = set(str(symbol) for symbol in expr.free_symbols)
        
        # Debug: imprimir las variables encontradas
        print(f"Variables encontradas: {found_vars}")
        print(f"Variables permitidas: {allowed_vars}")
        
        if found_vars and not found_vars.issubset(allowed_vars):
            invalid_vars = found_vars - allowed_vars
            return JsonResponse({"error": f"❌ Variables no permitidas: {', '.join(invalid_vars)}. Solo puedes usar x e y como variables. Las funciones como sqrt(x), sin(x), cos(x) SÍ están permitidas."})
    except Exception as e:
        error_msg = str(e)
        if "invalid syntax" in error_msg:
            return JsonResponse({"error": "Sintaxis inválida. Verifica que uses las funciones correctas: sin(x), cos(x), sqrt(x), etc."})
        elif "could not parse" in error_msg:
            return JsonResponse({"error": "No se pudo interpretar la expresión. Asegúrate de usar variables x e y."})
        elif "name" in error_msg and "is not defined" in error_msg:
            return JsonResponse({"error": "❌ Variable no definida. Solo usa x e y en tu expresión. Ejemplos válidos: x^2 + y^2, sin(x) + cos(y), sqrt(x^2 + y^2)"})
        else:
            return JsonResponse({"error": f"Expresión inválida: {error_msg}"})

    resultado = {}
    try:
        if operacion == "derivada_x":
            resultado["derivada"] = str(diff(expr, x))
        elif operacion == "derivada_y":
            resultado["derivada"] = str(diff(expr, y))
        elif operacion == "integral_doble":
            resultado["integral"] = str(integrate(expr, (x, -1, 1), (y, -1, 1)))
        elif operacion == "superficie":
            # Crear función lambda con manejo de errores
            f = lambdify((x, y), expr, ["numpy", "math"])
            X = np.linspace(-3, 3, 150)
            Y = np.linspace(-3, 3, 150)
            
            # Evaluar la función con manejo de errores
            Z = []
            for yi in Y:
                row = []
                for xi in X:
                    try:
                        val = f(xi, yi)
                        # Convertir a float primero para evitar problemas de tipos
                        val_float = float(val)
                        if np.isnan(val_float) or np.isinf(val_float):
                            row.append(0.0)  # Reemplazar valores inválidos con 0
                        else:
                            row.append(val_float)
                    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
                        row.append(0.0)  # Reemplazar errores con 0
                Z.append(row)
            
            resultado = {"x": list(X), "y": list(Y), "z": Z}
    except Exception as e:
        return JsonResponse({"error": f"Error al procesar la operación: {str(e)}"})

    return JsonResponse(resultado)