#!/bin/bash
set -e  # Detener si hay errores

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js
npm install

# Asegurar que webpack-cli esté instalado
npm install webpack webpack-cli --save

# Construir frontend con webpack (usando YES para auto-confirmar)
echo "yes" | npx webpack --mode production || npx webpack --mode production

# Recopilar archivos estáticos de Django
cd back
python manage.py collectstatic --noinput --clear
python manage.py migrate --noinput
cd ..
