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
        "derivative", "limit", "gradient", "domain", "range"
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
    x, y = symbols("x y")

    try:
        # --- SUPERFICIE LOCAL ---
        if op == "superficie":
            xmin = float(request.GET.get("xmin", -3))
            xmax = float(request.GET.get("xmax", 3))
            ymin = float(request.GET.get("ymin", -3))
            ymax = float(request.GET.get("ymax", 3))
            nx = int(request.GET.get("nx", 60))
            ny = int(request.GET.get("ny", 60))

            expr = sympify(expr_s_sym)
            f = lambdify((x, y), expr, "numpy")

            X = np.linspace(xmin, xmax, nx)
            Y = np.linspace(ymin, ymax, ny)
            XX, YY = np.meshgrid(X, Y)
            with np.errstate(all="ignore"):
                ZZ = f(XX, YY)
            ZZ = np.where(np.isfinite(ZZ), ZZ, np.nan)

            return JsonResponse({
                "x": X.tolist(),
                "y": Y.tolist(),
                "z": ZZ.tolist()
            })

        # --- OPERACIONES CON WOLFRAM ---
        elif op == "derivada_x":
            query = f"derivative of {expr_s} with respect to x"
        elif op == "derivada_y":
            query = f"derivative of {expr_s} with respect to y"
        elif op == "derivada_z":
            query = f"derivative of {expr_s} with respect to z"
        elif op == "integral_doble":
            query = f"double integral of {expr_s} dx dy"
        elif op == "integral_triple":
            query = f"triple integral of {expr_s} dx dy"
        elif op == "limite":
            a = request.GET.get("a", "0")
            b = request.GET.get("b", "0")
            query = f"limit of {expr_s} as x->{a} and y->{b}"
        elif op == "gradiente":
            query = f"gradient of {expr_s}"
        elif op == "dominio_rango":
            query = f"domain and range of {expr_s}"
        elif op == "lagrange":
            g = request.GET.get("g")
            c = request.GET.get("c")
            if not g or not c:
                return JsonResponse({"error": "g y c requeridos para Lagrange"})
            query = f"solve gradient of {expr_s} = lambda * gradient of {g} with constraint {g}={c}"
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
        elif op == "integral_triple":
            return JsonResponse({"integral_triple": valor})
        elif op == "limite":
            return JsonResponse({"limite": valor})
        elif op == "gradiente":
            return JsonResponse({"gradiente": valor})
        elif op == "dominio_rango":
            return JsonResponse({"dominio_rango": valor})
        elif op == "lagrange":
            return JsonResponse({"lagrange": valor})
        else:
            return JsonResponse({"resultado": valor})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
