"""
Script para probar el endpoint de campo de gradientes directamente
"""
import requests
import json

# URL del servidor Django (asegúrate de que esté corriendo)
url = "http://127.0.0.1:8000/api/calcular/"

# Parámetros para el campo de gradientes
params = {
    'expr': 'x^2 + y^2',
    'op': 'campo_gradiente',
    'xmin': '-3',
    'xmax': '3',
    'ymin': '-3',
    'ymax': '3',
    'grid_size': '10'
}

print("🔄 Haciendo petición al backend...")
print(f"URL: {url}")
print(f"Parámetros: {params}")
print("-" * 60)

try:
    response = requests.get(url, params=params)
    
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Respuesta exitosa")
        print(f"Type: {data.get('type')}")
        print(f"Número de vectores: {len(data.get('vectors', []))}")
        
        if data.get('vectors'):
            # Mostrar primer vector
            primer_vector = data['vectors'][0]
            print(f"\nPrimer vector:")
            print(f"  Posición: {primer_vector['position']}")
            print(f"  Gradiente: {primer_vector['gradient']}")
            print(f"  Magnitud: {primer_vector['magnitude']}")
            
            # Contar puntos críticos
            criticos = [v for v in data['vectors'] if v['magnitude'] < 0.01]
            print(f"\n🎯 Puntos críticos (magnitud < 0.01): {len(criticos)}")
            
            if criticos:
                print("Posiciones de puntos críticos:")
                for c in criticos:
                    print(f"  {c['position']}")
        
        # Guardar respuesta completa en archivo
        with open('respuesta_gradiente.json', 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Respuesta completa guardada en 'respuesta_gradiente.json'")
        
    else:
        print(f"\n❌ Error HTTP: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ No se pudo conectar al servidor")
    print("   Asegúrate de que Django esté corriendo en http://127.0.0.1:8000")
except Exception as e:
    print(f"❌ Error: {e}")
