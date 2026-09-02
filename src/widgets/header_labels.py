"""
Etiquetas de encabezado para las unidades de valor posicional:
- Español: CM, DM, UM (Naranja) y C, D, U (Blanco)
- Inglés: HTh, TTh, Th (Naranja) y H, T, O (Blanco)
"""

from PyQt6.QtCore import Qt, QSize, QRectF, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QWidget, QHBoxLayout


class PositionTag(QWidget):
    TOOLTIPS_ES = {
        "CM": "Centenas de Mil = 100.000 unidades",
        "DM": "Decenas de Mil = 10.000 unidades",
        "UM": "Unidades de Mil = 1.000 unidades",
        "C": "Centenas = 100 unidades",
        "D": "Decenas = 10 unidades",
        "U": "Unidades = 1 unidad"
    }

    TOOLTIPS_EN = {
        "HTh": "Hundred Thousands = 100,000 units",
        "TTh": "Ten Thousands = 10,000 units",
        "Th": "Thousands = 1,000 units",
        "H": "Hundreds = 100 units",
        "T": "Tens = 10 units",
        "O": "Ones = 1 unit"
    }

    def __init__(self, text: str, is_mil: bool, lang: str = "es", parent=None):
        super().__init__(parent)
        self.text = text
        self.is_mil = is_mil
        self.lang = lang
        self._highlight = 0.0

        self._update_tooltip()
        self.setMinimumSize(74, 52)

    def _update_tooltip(self):
        tips = self.TOOLTIPS_EN if self.lang == "en" else self.TOOLTIPS_ES
        self.setToolTip(tips.get(self.text, self.text))

    def set_label_text(self, text: str, lang: str):
        self.text = text
        self.lang = lang
        self._update_tooltip()
        self.update()

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
            base_bg = QColor(227, 94, 40)
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
            base_bg = QColor(255, 255, 255)
            if self._highlight > 0:
                bg_color = QColor(255, int(255 - 40 * self._highlight), int(255 - 70 * self._highlight))
            else:
                bg_color = base_bg
            border_pen = QPen(QColor(70, 100, 120), 1.3)
            text_color = QColor(10, 10, 10)

        painter.setPen(border_pen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(rect)

        # Ajuste de tamaño de fuente según longitud (ej. HTh o TTh)
        factor = 0.30 if len(self.text) >= 3 else 0.40
        font_size = min(w * factor, h * 0.54)
        font = QFont("sans-serif", int(font_size), QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text)


class HeaderRow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        self.configs = [
            ("CM", True),
            ("DM", True),
            ("UM", True),
            ("C", False),
            ("D", False),
            ("U", False)
        ]

        for name, is_mil in self.configs:
            tag = PositionTag(name, is_mil, lang="es", parent=self)
            self.tags.append(tag)
            layout.addWidget(tag)

    def pulse_index(self, idx: int):
        # idx: 0 a 5 de izquierda a derecha
        if 0 <= idx < len(self.tags):
            self.tags[idx].trigger_pulse()

    def update_language(self, lang: str):
        if lang == "en":
            names = ["HTh", "TTh", "Th", "H", "T", "O"]
        else:
            names = ["CM", "DM", "UM", "C", "D", "U"]

        for i, name in enumerate(names):
            self.tags[i].set_label_text(name, lang)
