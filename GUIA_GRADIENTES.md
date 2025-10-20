# 🎯 Guía de Uso: Campo de Gradientes

## ✅ Implementación Completa

La funcionalidad de **Campo de Gradientes** está completamente implementada y lista para usar.

## 📋 Cómo Usar

### 1. Iniciar el Servidor
```bash
cd back
python manage.py runserver
```

### 2. Abrir el Navegador
Ir a: `http://127.0.0.1:8000`

### 3. Configurar el Campo de Gradientes

**Paso 1:** Seleccionar **"Campo de gradientes"** en el menú desplegable

**Paso 2:** Ingresar una función matemática (solo con x, y):
- Ejemplos recomendados:
  - `x^2 + y^2` → Paraboloide (mínimo en origen)
  - `x^2 - y^2` → Silla de montar (punto silla en origen)
  - `-x^2 - y^2` → Paraboloide invertido (máximo en origen)
  - `sin(x) + cos(y)` → Función ondulada (múltiples extremos)

**Paso 3:** Ajustar parámetros:
- **Rango X**: -3 a 3 (por defecto)
- **Rango Y**: -3 a 3 (por defecto)
- **Densidad**: 10 (recomendado 8-15)
  - Menor = Menos flechas, más claridad
  - Mayor = Más flechas, más detalle

**Paso 4:** Click en **"Calcular"**

## 🎨 Interpretación Visual

### Flechas (Vectores del Gradiente)
- **Dirección**: Hacia donde crece más rápido la función
- **Color**:
  - 🔵 **Azul**: Magnitud baja (cambio lento)
  - 🟢 **Verde**: Magnitud media
  - 🟡 **Amarillo**: Magnitud alta
  - 🔴 **Rojo**: Magnitud muy alta (cambio rápido)
- **Longitud**: Proporcional a la magnitud del gradiente

### Esferas Amarillas 🟡
- Marcan **puntos críticos** donde ∇f ≈ 0
- Pueden ser:
  - **Mínimos locales**: Las flechas alrededor apuntan hacia fuera
  - **Máximos locales**: Las flechas alrededor apuntan hacia dentro
  - **Puntos silla**: Las flechas tienen direcciones mixtas

## 📊 Ejemplos de Visualización

### Paraboloide: `x^2 + y^2`
```
Resultado esperado:
- 1 esfera amarilla en el origen (mínimo)
- Flechas apuntan radialmente hacia afuera
- Colores más cálidos lejos del origen
```

### Silla de Montar: `x^2 - y^2`
```
Resultado esperado:
- 1 esfera amarilla en el origen (punto silla)
- Flechas apuntan en 4 direcciones principales
- Patrón de "X" con las flechas
```

### Función con Múltiples Extremos: `sin(x)*cos(y)`
```
Resultado esperado:
- Múltiples esferas amarillas (máximos y mínimos)
- Patrón ondulado de flechas
- Alternancia entre zonas de crecimiento y decrecimiento
```

## 🔧 Controles 3D

- **Rotar**: Click izquierdo + arrastrar
- **Zoom**: Rueda del ratón
- **Pan**: Click derecho + arrastrar
- **Cambiar tema**: Botón 🌙/☀️ (esquina superior)

## ⚠️ Notas Importantes

1. **Solo funciones z = f(x, y)**: No usar `z` en la expresión
2. **Densidad óptima**: 8-15 para buena visualización
3. **Rango apropiado**: Ajustar según la función para ver los puntos de interés
4. **Puntos críticos**: Las esferas amarillas son los candidatos a extremos

## 🎓 Aplicaciones Matemáticas

### Encontrar Extremos
1. Graficar el campo de gradientes
2. Buscar las esferas amarillas (∇f = 0)
3. Observar las flechas alrededor para clasificar:
   - Todas apuntan hacia afuera → **Mínimo**
   - Todas apuntan hacia dentro → **Máximo**
   - Direcciones mixtas → **Punto silla**

### Estudiar Comportamiento
- **Flechas largas y rojas**: Zonas de cambio rápido
- **Flechas cortas y azules**: Zonas planas
- **Dirección de flechas**: Dirección de máximo crecimiento

## 🐛 Resolución de Problemas

**No se ven las flechas:**
- Verificar que la función sea válida
- Probar con densidad más baja (5-7)
- Ajustar el rango para incluir puntos de interés

**Demasiadas flechas:**
- Reducir la densidad a 6-8
- Ajustar el rango a una zona más pequeña

**No aparecen esferas amarillas:**
- La función no tiene puntos críticos en el rango especificado
- Probar con un rango más amplio o función diferente

## ✅ Verificación

Para verificar que todo funciona:
1. Usar función `x^2 + y^2`
2. Rango: -2 a 2 en X e Y
3. Densidad: 10
4. Debes ver: 1 esfera amarilla en (0,0) y ~100 flechas apuntando hacia afuera

---

**¿Todo listo?** ¡Inicia el servidor y prueba la nueva funcionalidad! 🚀
