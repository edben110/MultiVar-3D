#!/bin/bash

# Instalar dependencias de Python
pip install -r requirements.txt

# Instalar Node.js y npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar dependencias de Node.js de la raíz
npm install

# Construir frontend con webpack desde la raíz
npx webpack --mode production

# Entrar a back e instalar dependencias
cd back
npm install
cd ..

# Collect static y migraciones de Django
python back/manage.py collectstatic --noinput
python back/manage.py migrate
