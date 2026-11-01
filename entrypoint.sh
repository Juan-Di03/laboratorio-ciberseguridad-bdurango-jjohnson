#!/bin/sh
set -eu

APP="/app/app.py"

if [ ! -f "$APP" ]; then
  echo "Error: no se encontr? la aplicaci?n en $APP" >&2
  exit 1
fi

exec python "$APP"
