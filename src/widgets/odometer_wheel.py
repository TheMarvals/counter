"""
Widget de rueda cilíndrica de odómetro mecánico en 3D.
Solo anima la rueda cuando su propio dígito cambia de valor.
"""

import math
from PyQt6.QtCore import (
    Qt, pyqtSignal, QVariantAnimation, QEasingCurve, QRectF, QPointF, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QLinearGradient, QFont, QPen, QBrush
)
from PyQt6.QtWidgets import QWidget


class OdometerWheel(QWidget):
    incrementRequested = pyqtSignal()
    decrementRequested = pyqtSignal()

    def __init__(self, pos_name: str = "U", parent=None):
        super().__init__(parent)
        self.pos_name = pos_name
        self._current_val = 0.0
        self._target_val = 0.0

        self._animation = QVariantAnimation(self)
        self._animation.setDuration(240)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.valueChanged.connect(self._on_anim_step)
        self._animation.finished.connect(self._on_anim_finished)

        self._drag_start_y = None
        self._drag_accum = 0.0

        self.setMinimumSize(78, 148)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def sizeHint(self):
        return QSize(86, 154)

    def set_digit(self, digit: int, animated: bool = True, direction: int = 1):
        digit = digit % 10
        current_int = int(round(self._current_val)) % 10

        # Si el dígito NO cambió, no hacer nada (no rotar)
        if current_int == digit and not self._animation.state() == QVariantAnimation.State.Running:
            self._current_val = float(digit)
            self._target_val = float(digit)
            self.update()
            return

        if not animated:
            self._animation.stop()
            self._current_val = float(digit)
            self._target_val = float(digit)
            self.update()
            return

        # Calcular únicamente el desplazamiento necesario
        start_val = self._current_val
        current_mod = start_val % 10.0

        if direction > 0:
            # Giro hacia arriba (sumar)
            diff = (digit - current_mod) % 10.0
            if diff == 0:
                # Ya está en el valor
                self._current_val = float(digit)
                self.update()
                return
            end_val = start_val + diff
        elif direction < 0:
            # Giro hacia abajo (restar)
            diff = (current_mod - digit) % 10.0
            if diff == 0:
                self._current_val = float(digit)
                self.update()
                return
            end_val = start_val - diff
        else:
            diff = digit - current_mod
            end_val = start_val + diff

        self._animation.stop()
        self._animation.setStartValue(start_val)
        self._animation.setEndValue(end_val)
        self._animation.start()

    def _on_anim_step(self, val):
        self._current_val = float(val)
        self.update()

    def _on_anim_finished(self):
        self._current_val = self._current_val % 10.0
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.incrementRequested.emit()
        elif delta < 0:
            self.decrementRequested.emit()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_y = event.position().y()
            self._drag_accum = 0.0
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_start_y is not None:
            dy = event.position().y() - self._drag_start_y
            self._drag_accum += dy
            self._drag_start_y = event.position().y()

            threshold = 28.0
            if self._drag_accum < -threshold:
                self.incrementRequested.emit()
                self._drag_accum = 0.0
            elif self._drag_accum > threshold:
                self.decrementRequested.emit()
                self._drag_accum = 0.0
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_start_y = None
        self._drag_accum = 0.0
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        w = float(self.width())
        h = float(self.height())

        drum_rect = QRectF(1.5, 1.5, w - 3, h - 3)

        # 1. Fondo del tambor cilíndrico
        grad = QLinearGradient(0, 1, 0, h - 1)
        grad.setColorAt(0.00, QColor(10, 10, 12))
        grad.setColorAt(0.12, QColor(32, 34, 38))
        grad.setColorAt(0.38, QColor(56, 60, 66))
        grad.setColorAt(0.50, QColor(76, 80, 88))
        grad.setColorAt(0.62, QColor(56, 60, 66))
        grad.setColorAt(0.88, QColor(32, 34, 38))
        grad.setColorAt(1.00, QColor(10, 10, 12))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(drum_rect, 3.0, 3.0)

        # 2. Sombras laterales para distinguir cilindros individuales
        side_grad = QLinearGradient(1, 0, w - 1, 0)
        side_grad.setColorAt(0.00, QColor(0, 0, 0, 170))
        side_grad.setColorAt(0.08, QColor(0, 0, 0, 30))
        side_grad.setColorAt(0.92, QColor(0, 0, 0, 30))
        side_grad.setColorAt(1.00, QColor(0, 0, 0, 170))
        painter.setBrush(QBrush(side_grad))
        painter.drawRoundedRect(drum_rect, 3.0, 3.0)

        # 3. Reflejo horizontal en el centro
        mid_y = h * 0.5
        highlight_pen = QPen(QColor(255, 255, 255, 38))
        highlight_pen.setWidthF(1.2)
        painter.setPen(highlight_pen)
        painter.drawLine(QPointF(3, mid_y), QPointF(w - 3, mid_y))

        # 4. Números con perspectiva cilíndrica
        center_val = self._current_val % 10.0
        base_int = int(math.floor(center_val))
        frac = center_val - base_int

        font_size = min(w * 0.74, h * 0.44)
        font = QFont("sans-serif", int(font_size), QFont.Weight.Bold)
        font.setFamilies(["Helvetica Neue", "Arial", "DejaVu Sans", "sans-serif"])
        painter.setFont(font)

        slot_height = h * 0.58

        painter.save()
        painter.setClipRect(drum_rect)

        for offset in [-1, 0, 1]:
            digit_to_draw = (base_int + offset) % 10
            y_offset = (offset - frac) * slot_height
            curr_y = mid_y + y_offset

            norm_y = y_offset / (h * 0.5)
            if abs(norm_y) > 1.4:
                continue

            scale_y = math.cos(max(-1.45, min(1.45, norm_y * 1.05)))
            scale_y = max(0.25, scale_y)
            alpha = int(255 * (scale_y ** 1.8))
            alpha = max(15, min(255, alpha))

            painter.save()
            painter.translate(w * 0.5, curr_y)
            painter.scale(1.0, scale_y)

            text = str(digit_to_draw)
            text_rect = QRectF(-w * 0.5, -font_size * 0.65, w, font_size * 1.3)

            painter.setPen(QColor(0, 0, 0, int(alpha * 0.7)))
            painter.drawText(text_rect.translated(0, 2), Qt.AlignmentFlag.AlignCenter, text)

            painter.setPen(QColor(248, 248, 250, alpha))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)
            painter.restore()

        painter.restore()

        # 5. Bisel de oclusión superior e inferior
        top_shadow = QLinearGradient(0, 1, 0, 26)
        top_shadow.setColorAt(0.0, QColor(0, 0, 0, 225))
        top_shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(top_shadow))
        painter.drawRect(QRectF(1.5, 1.5, w - 3, 24))

        bot_shadow = QLinearGradient(0, h - 26, 0, h - 1)
        bot_shadow.setColorAt(0.0, QColor(0, 0, 0, 0))
        bot_shadow.setColorAt(1.0, QColor(0, 0, 0, 225))
        painter.setBrush(QBrush(bot_shadow))
        painter.drawRect(QRectF(1.5, h - 26, w - 3, 24))

        # 6. Borde exterior
        frame_pen = QPen(QColor(45, 48, 54), 1.0)
        painter.setPen(frame_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(drum_rect, 3.0, 3.0)
