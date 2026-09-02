#!/usr/bin/env bash
# Script para compilar la aplicación en un único archivo ejecutable independiente
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "Compilando Contador de Unidades en un solo ejecutable independiente..."

QT6_PLUGINS="/usr/lib/x86_64-linux-gnu/qt6/plugins"
EXTRA_ARGS=()

if [ -d "$QT6_PLUGINS" ]; then
    # Incluir todas las carpetas clave de plugins de Qt6
    for sub in platforms wayland-shell-integration wayland-graphics-integration-client wayland-decoration-client xcbglintegrations platformthemes imageformats iconengines; do
        if [ -d "$QT6_PLUGINS/$sub" ]; then
            EXTRA_ARGS+=(--add-binary "$QT6_PLUGINS/$sub/*:PyQt6/Qt6/plugins/$sub")
        fi
    done
fi

python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name "ContadorDeUnidades" \
    --add-data "assets:assets" \
    "${EXTRA_ARGS[@]}" \
    --clean \
    main.py

echo ""
echo "¡Compilación exitosa!"
echo "Ejecutable único generado en: dist/ContadorDeUnidades"
