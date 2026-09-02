#!/usr/bin/env python3
"""
Punto de entrada para la aplicación de escritorio del Contador de Unidades para Niños.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Si estamos en Linux Wayland/X11, configurar la plataforma con fallback automático a xcb
if sys.platform.startswith("linux") and "QT_QPA_PLATFORM" not in os.environ:
    # Intenta wayland, y si falla la integración de shell, usa xcb inmediatamente
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"

# Configurar ruta de plugins de Qt en ejecutables empaquetados por PyInstaller
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    qt_plugin_path = os.path.join(sys._MEIPASS, "PyQt6", "Qt6", "plugins")
    if os.path.exists(qt_plugin_path):
        os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Contador de Unidades")
    app.setApplicationDisplayName("Contador de Unidades y Valor Posicional")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
