#!/bin/sh

# Dirección del servidor objetivo en la DMZ
TARGET="https://servidor-web-dmz-ebl.onrender.com"

# Diccionario reducido de rutas sensibles para la prueba
RUTAS="/admin /config.php /login /secret /backup.zip /index.html"

echo "=== INICIANDO ENUMERACIÓN DE RUTAS EN LA DMZ ==="
echo "Probando peticiones HTTP a rutas conocidas..."

for ruta in $RUTAS; do
  CODE=$(curl -o /dev/null -s -w "%{http_code}" "$TARGET$ruta")
  echo "Ruta probada: $ruta -> Código de respuesta HTTP: $CODE"
done

echo "=== ENUMERACIÓN DE RUTAS FINALIZADA ==="

# Mantener activo el contenedor para Render
python3 -m http.server 8080
