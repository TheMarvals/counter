#!/usr/bin/env bash
# Lanzador de macOS para el Contador de Unidades
# Puedes hacer doble clic en este archivo en macOS para iniciar la aplicación.

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Verificar python3
if command -v python3 >/dev/null 2>&1; then
    exec python3 main.py
else
    echo "Python 3 no encontrado. Por favor instala Python 3 desde https://www.python.org"
    read -p "Presiona Enter para cerrar..."
fi
