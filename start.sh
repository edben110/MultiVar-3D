#!/bin/bash

# Cambiar al directorio del proyecto Django
cd back

# Ejecutar gunicorn
exec gunicorn back.wsgi:application --bind 0.0.0.0:$PORT
