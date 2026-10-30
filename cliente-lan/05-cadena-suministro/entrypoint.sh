#!/bin/sh

echo "=== INICIANDO SERVICIO COMPROMETIDO EN LA CADENA DE SUMINISTRO ==="
echo "Verificando integridad del contenedor..."

# Verificamos si la dependencia alterada inyectó el script malicioso
if [ -f "/app/malicious_dependency.sh" ]; then
  echo "[ALERTA DE SEGURIDAD] Se ha detectado una dependencia no autorizada inyectada durante la construcción del artefacto."
  sh /app/malicious_dependency.sh
else
  echo "[OK] Artefacto limpio."
fi

# Mantener activo el contenedor
python3 -m http.server 8080
