#!/usr/bin/env bash
# Script de inicio para el Contador de Unidades para Niños
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Ejecutar con python3
exec python3 main.py "$@"
