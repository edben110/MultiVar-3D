#!/bin/bash

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar dependencias de Node.js de la raíz
npm install

# Construir frontend con webpack desde la raíz
npx webpack --mode production

# Recopilar archivos estáticos de Django
cd back
python manage.py collectstatic --noinput
cd ..

# Collect static y migraciones de Django
python back/manage.py collectstatic --noinput
python back/manage.py migrate
