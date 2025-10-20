#!/bin/bash
set -e  # Detener si hay errores

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js
npm install

# Construir frontend con webpack
npx webpack --mode production

# Recopilar archivos estáticos de Django
cd back
python manage.py collectstatic --noinput --clear
python manage.py migrate --noinput
cd ..
