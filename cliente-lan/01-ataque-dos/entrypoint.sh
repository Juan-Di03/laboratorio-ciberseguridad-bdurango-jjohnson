#!/bin/sh
TARGET="https://servidor-web-dmz-ebl.onrender.com"

echo "=== SIMULACIÓN: GENERANDO TRÁFICO MASIVO HTTP ==="
for i in $(seq 1 30); do
  curl -s -o /dev/null "$TARGET" &
done
wait

echo "=== PRUEBA FINALIZADA ==="
python3 -m http.server 8080
