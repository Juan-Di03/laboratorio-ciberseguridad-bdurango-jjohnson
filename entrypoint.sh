#!/bin/sh
apk add --no-cache curl bind-tools
echo "=== PRUEBA DNS ==="
nslookup servidor-web-dmz.onrender.com
echo "=== PRUEBA HTTP ==="
curl -I https://servidor-web-dmz.onrender.com
echo "=== INICIANDO SERVIDOR ==="
python -m http.server 8080
