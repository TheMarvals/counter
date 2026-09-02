"""
Etiquetas de encabezado para las unidades de valor posicional:
CM, DM, UM (Naranja) y C, D, U (Blanco).
Idénticas al diseño de referencia con realce visual interactivo.
"""

from PyQt6.QtCore import Qt, QSize, QRectF, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QWidget, QHBoxLayout


class PositionTag(QWidget):
    TOOLTIPS = {
        "CM": "Centenas de Mil = 100.000 unidades",
        "DM": "Decenas de Mil = 10.000 unidades",
        "UM": "Unidades de Mil = 1.000 unidades",
        "C": "Centenas = 100 unidades",
        "D": "Decenas = 10 unidades",
        "U": "Unidades = 1 unidad"
    }

    def __init__(self, text: str, is_mil: bool, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_mil = is_mil
        self._highlight = 0.0

        self.setToolTip(self.TOOLTIPS.get(text, text))
        self.setMinimumSize(74, 52)

    def sizeHint(self):
        return QSize(86, 56)

    def get_highlight(self) -> float:
        return self._highlight

    def set_highlight(self, val: float):
        self._highlight = val
        self.update()

    highlight = pyqtProperty(float, get_highlight, set_highlight)

    def trigger_pulse(self):
        self.anim = QPropertyAnimation(self, b"highlight")
        self.anim.setDuration(320)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(2, 2, w - 4, h - 4)

        if self.is_mil:
            base_bg = QColor(227, 94, 40)  # Naranja cálido
            if self._highlight > 0:
                r = int(base_bg.red() + (255 - base_bg.red()) * self._highlight)
                g = int(base_bg.green() + (230 - base_bg.green()) * self._highlight)
                b = int(base_bg.blue() * (1.0 - self._highlight))
                bg_color = QColor(r, g, b)
            else:
                bg_color = base_bg
            border_pen = QPen(QColor(130, 45, 12), 1.5)
            text_color = QColor(10, 10, 10)
        else:
            base_bg = QColor(255, 255, 255)  # Blanco puro
            if self._highlight > 0:
                bg_color = QColor(255, int(255 - 40 * self._highlight), int(255 - 70 * self._highlight))
            else:
                bg_color = base_bg
            border_pen = QPen(QColor(70, 100, 120), 1.3)
            text_color = QColor(10, 10, 10)

        painter.setPen(border_pen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(rect)

        font_size = min(w * 0.40, h * 0.54)
        font = QFont("DejaVu Sans", int(font_size), QFont.Weight.Bold)
        if not font.exactMatch():
            font = QFont("sans-serif", int(font_size), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text)


class HeaderRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.labels = {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        configs = [
            ("CM", True),
            ("DM", True),
            ("UM", True),
            ("C", False),
            ("D", False),
            ("U", False)
        ]

        for name, is_mil in configs:
            tag = PositionTag(name, is_mil, self)
            self.labels[name] = tag
            layout.addWidget(tag)

    def pulse_column(self, col_name: str):
        if col_name in self.labels:
            self.labels[col_name].trigger_pulse()
