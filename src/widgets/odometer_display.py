"""
Conjunto completo del odómetro:
- Encabezados bilingües: CM..U (ES) o HTh..O (EN)
- Flechas superiores (▲) e inferiores (▼)
- Soporte para Modo Automático y Modo Manual
- Separador de miles correcto: punto '.' en español o coma ',' en inglés cuando >= 1.000
"""

from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame
)

from src.widgets.odometer_wheel import OdometerWheel
from src.widgets.triangle_button import TriangleButton
from src.widgets.header_labels import HeaderRow
from src.audio.sound_player import SoundPlayer


class DrumFrame(QFrame):
    def __init__(self, wheels: list[OdometerWheel], model, parent=None):
        super().__init__(parent)
        self.wheels = wheels
        self.model = model
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 8, 10, 8)
        self.layout.setSpacing(6)

        for w in self.wheels:
            self.layout.addWidget(w)

        self.setStyleSheet("""
            DrumFrame {
                background-color: #1a1a1c;
                border: 3px solid #7c828c;
                border-radius: 6px;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)

        # Separador de miles entre UM (índice 2) y C (índice 3) cuando >= 1.000
        if self.model.value >= 1000 and len(self.wheels) >= 4:
            um_wheel = self.wheels[2]
            c_wheel = self.wheels[3]

            if um_wheel.isVisible() and c_wheel.isVisible():
                um_right = float(um_wheel.geometry().right())
                c_left = float(c_wheel.geometry().left())
                mid_x = (um_right + c_left) * 0.5
                mid_y = float(self.height()) * 0.5

                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                # Signo de puntuación según el idioma
                if self.model.lang == "en":
                    # Coma en inglés ','
                    font = QFont("sans-serif", 20, QFont.Weight.Bold)
                    painter.setFont(font)
                    painter.setPen(QColor(230, 230, 235, 230))
                    painter.drawText(QRectF(mid_x - 6, mid_y + 4, 12, 20), Qt.AlignmentFlag.AlignCenter, ",")
                else:
                    # Punto en español '.'
                    dot_size = 6.0
                    point_rect = QRectF(mid_x - dot_size * 0.5, mid_y + 16.0, dot_size, dot_size)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(230, 230, 235, 230))
                    painter.drawEllipse(point_rect)


class FloorShadow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)

    def paintEvent(self, event):
        from PyQt6.QtGui import QRadialGradient
        from PyQt6.QtCore import QPointF
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        center_x = w * 0.5
        center_y = h * 0.35
        rad_x = w * 0.44
        rad_y = h * 0.44

        grad = QRadialGradient(center_x, center_y, rad_x)
        grad.setColorAt(0.00, QColor(0, 0, 0, 115))
        grad.setColorAt(0.35, QColor(0, 0, 0, 60))
        grad.setColorAt(0.70, QColor(0, 0, 0, 18))
        grad.setColorAt(1.00, QColor(0, 0, 0, 0))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(QPointF(center_x, center_y), rad_x, rad_y)


class OdometerDisplay(QWidget):
    columnIncremented = pyqtSignal(int)
    columnDecremented = pyqtSignal(int)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.sound_player = SoundPlayer.get_instance()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(14)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. Encabezados
        self.header_row = HeaderRow(self)
        main_layout.addWidget(self.header_row)

        # 2. Flechas superiores (▲)
        self.up_buttons_layout = QHBoxLayout()
        self.up_buttons_layout.setContentsMargins(10, 0, 10, 0)
        self.up_buttons_layout.setSpacing(6)
        self.up_buttons = []

        # 3. Tambores mecánicos (índices visuales 0 a 5 -> modelos 5, 4, 3, 2, 1, 0)
        self.wheels = []
        self.model_indices = [5, 4, 3, 2, 1, 0]

        for visual_idx, m_idx in enumerate(self.model_indices):
            btn_up = TriangleButton(direction="up")
            btn_up.clicked.connect(lambda checked, idx=m_idx, v_idx=visual_idx: self._on_up_clicked(idx, v_idx))
            self.up_buttons.append(btn_up)
            self.up_buttons_layout.addWidget(btn_up)

            wheel = OdometerWheel()
            wheel.incrementRequested.connect(lambda idx=m_idx, v_idx=visual_idx: self._on_up_clicked(idx, v_idx))
            wheel.decrementRequested.connect(lambda idx=m_idx, v_idx=visual_idx: self._on_down_clicked(idx, v_idx))
            self.wheels.append(wheel)

        main_layout.addLayout(self.up_buttons_layout)

        # Marco del tambor
        self.drum_frame = DrumFrame(self.wheels, self.model)
        main_layout.addWidget(self.drum_frame)

        # 4. Flechas inferiores (▼)
        self.down_buttons_layout = QHBoxLayout()
        self.down_buttons_layout.setContentsMargins(10, 0, 10, 0)
        self.down_buttons_layout.setSpacing(6)
        self.down_buttons = []

        for visual_idx, m_idx in enumerate(self.model_indices):
            btn_down = TriangleButton(direction="down")
            btn_down.clicked.connect(lambda checked, idx=m_idx, v_idx=visual_idx: self._on_down_clicked(idx, v_idx))
            self.down_buttons.append(btn_down)
            self.down_buttons_layout.addWidget(btn_down)

        main_layout.addLayout(self.down_buttons_layout)

        # 5. Sombra inferior
        self.floor_shadow = FloorShadow()
        main_layout.addWidget(self.floor_shadow)

        self.model.valueChanged.connect(self._on_model_value_changed)
        self.model.displayConfigChanged.connect(self._on_display_config_changed)

        self._sync_digits(animated=False)
        self._update_column_visibility()

    def _on_up_clicked(self, pos_idx: int, visual_idx: int):
        self.sound_player.play_click()
        self.header_row.pulse_index(visual_idx)
        self.columnIncremented.emit(pos_idx)
        self.model.increment_column(pos_idx)

    def _on_down_clicked(self, pos_idx: int, visual_idx: int):
        self.sound_player.play_click()
        self.header_row.pulse_index(visual_idx)
        self.columnDecremented.emit(pos_idx)
        self.model.decrement_column(pos_idx)

    def _on_model_value_changed(self, new_val: int, digits: list[int], info: dict):
        old_val = info.get("old_value", new_val)
        reason = info.get("reason", "")
        direction = 1 if new_val >= old_val else -1

        animated = reason != "direct" and reason != "reset"

        for i, digit in enumerate(digits):
            self.wheels[i].set_digit(digit, animated=animated, direction=direction)

        self._update_column_visibility()
        self.drum_frame.update()

    def _on_display_config_changed(self):
        self.header_row.update_language(self.model.lang)
        self._update_column_visibility()
        self.drum_frame.update()

    def _sync_digits(self, animated: bool = False):
        digits = self.model.get_digits()
        for i, digit in enumerate(digits):
            self.wheels[i].set_digit(digit, animated=animated)

    def _update_column_visibility(self):
        active_count = self.model.active_digits
        val = self.model.value

        if self.model.hide_leading_zeros:
            if val == 0:
                needed = 1
            else:
                needed = len(str(val))
            visible_count = min(active_count, max(1, needed))
        else:
            visible_count = active_count

        start_visible_idx = 6 - visible_count

        for i in range(6):
            is_visible = (i >= start_visible_idx)
            self.wheels[i].setVisible(is_visible)
            self.up_buttons[i].setVisible(is_visible)
            self.down_buttons[i].setVisible(is_visible)
            self.header_row.tags[i].setVisible(is_visible)

        self.drum_frame.update()
