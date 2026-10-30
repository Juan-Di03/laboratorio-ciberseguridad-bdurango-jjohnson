#!/bin/sh

# Dirección del servidor objetivo en la DMZ
HOST="https://servidor-web-dmz-ebl.onrender.com"

echo "=== INICIANDO ESCANEO DE PUERTOS Y RECONOCIMIENTO EN LA DMZ ==="
echo "Analizando puertos comunes..."

# Lista de puertos a escanear: 21 (FTP), 22 (SSH), 80 (HTTP), 443 (HTTPS), 8080 (Web Alt), 3306 (MySQL)
for port in 21 22 80 443 8080 3306; do
  nc -zv -w 2 $HOST $port 2>&1
done

echo "=== ESCANEO DE PUERTOS FINALIZADO ==="

# Mantener el contenedor activo para Render
python3 -m http.server 8080
