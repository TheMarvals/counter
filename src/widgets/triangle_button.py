"""
Botón en forma de triángulo estilizado (▲ / ▼) en color azul petróleo/teal,
idéntico al diseño de referencia.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QSize
from PyQt6.QtGui import QPainter, QColor, QPolygonF, QBrush, QPen, QLinearGradient
from PyQt6.QtWidgets import QAbstractButton


class TriangleButton(QAbstractButton):
    def __init__(self, direction: str = "up", parent=None):
        super().__init__(parent)
        self.direction = direction  # "up" o "down"
        self._hovered = False
        self._pressed = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumSize(46, 38)

    def sizeHint(self):
        return QSize(54, 42)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # Colores según el diseño: azul petróleo/teal oscuro
        base_color = QColor(22, 94, 125)        # #165E7D
        hover_color = QColor(32, 128, 170)      # Más brillante al posar el ratón
        pressed_color = QColor(14, 66, 88)      # Más oscuro al pulsar

        if self._pressed:
            fill_color = pressed_color
        elif self._hovered:
            fill_color = hover_color
        else:
            fill_color = base_color

        # Definir los tres vértices del triángulo
        pad_x = w * 0.16
        pad_y = h * 0.14

        if self.direction == "up":
            # Apunta hacia arriba (▲)
            p1 = QPointF(w * 0.5, pad_y)              # Vértice superior
            p2 = QPointF(pad_x, h - pad_y)             # Inferior izquierdo
            p3 = QPointF(w - pad_x, h - pad_y)         # Inferior derecho
        else:
            # Apunta hacia abajo (▼)
            p1 = QPointF(w * 0.5, h - pad_y)          # Vértice inferior
            p2 = QPointF(pad_x, pad_y)                 # Superior izquierdo
            p3 = QPointF(w - pad_x, pad_y)             # Superior derecho

        triangle = QPolygonF([p1, p2, p3])

        # Sombra sutil
        painter.save()
        painter.translate(0, 2)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(0, 0, 0, 45))
        painter.drawPolygon(triangle)
        painter.restore()

        # Gradiente suave en el triángulo
        grad = QLinearGradient(p1, QPointF(w * 0.5, (p2.y() + p3.y()) * 0.5))
        if self.direction == "up":
            grad.setColorAt(0.0, fill_color.lighter(125))
            grad.setColorAt(1.0, fill_color.darker(115))
        else:
            grad.setColorAt(0.0, fill_color.darker(115))
            grad.setColorAt(1.0, fill_color.lighter(125))

        painter.setBrush(QBrush(grad))
        border_color = fill_color.darker(140)
        painter.setPen(QPen(border_color, 1.4))
        painter.drawPolygon(triangle)
