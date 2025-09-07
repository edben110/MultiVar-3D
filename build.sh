#!/bin/bash

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar Node.js y npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar dependencias de Node.js de la raíz
npm install

# Entrar a back y construir frontend con npm
cd back
npm install
npm run build
cd ..

# Collect static y migraciones de Django
python back/manage.py collectstatic --noinput
python back/manage.py migrate
