from django.shortcuts import render
from django.http import JsonResponse
from sympy import symbols, sympify, diff, integrate, lambdify
import numpy as np
import re

def index(request):
    return render(request, "index.html")

def calcular(request):
    expr_str = request.GET.get("expr", "x^2 + y^2")
    operacion = request.GET.get("op", "superficie")

    # Normalizar expresión para Sympy
    expr_str = expr_str.replace("^", "**").lower()
    # Insertar multiplicaciones implícitas
    expr_str = re.sub(r'(\d)(\s*)([a-zA-Z])', r'\1*\3', expr_str)
    expr_str = re.sub(r'([a-zA-Z])(\s+)([a-zA-Z])', r'\1*\3', expr_str)
    expr_str = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr_str)

    x, y = symbols("x y")
    try:
        expr = sympify(expr_str)
    except Exception as e:
        return JsonResponse({"error": f"Expresión inválida: {str(e)}"})

    resultado = {}
    if operacion == "derivada_x":
        resultado["derivada"] = str(diff(expr, x))
    elif operacion == "derivada_y":
        resultado["derivada"] = str(diff(expr, y))
    elif operacion == "integral_doble":
        resultado["integral"] = str(integrate(expr, (x, -1, 1), (y, -1, 1)))
    elif operacion == "superficie":
        f = lambdify((x, y), expr, "numpy")
        X = np.linspace(-5, 5, 200)
        Y = np.linspace(-5, 5, 200)
        Z = [[float(f(xi, yi)) for xi in X] for yi in Y]
        resultado = {"x": list(X), "y": list(Y), "z": Z}

    return JsonResponse(resultado)
