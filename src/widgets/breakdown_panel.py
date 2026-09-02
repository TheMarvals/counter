"""
Panel pedagógico de desglose del valor posicional para niños:
- Descomposición aditiva visual sin ceros a la izquierda ni ceros innecesarios
- Signos de puntuación correctos en las cifras (punto de miles)
- Lectura en palabras en español
- Botón de audio para escuchar la pronunciación (compatible con Linux y macOS)
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)

from src.model.number_words import (
    numero_a_palabras, descomposicion_aditiva, formatear_cifra_es
)
from src.audio.sound_player import SoundPlayer


class ValueChip(QFrame):
    def __init__(self, pos_name: str, value_text: str, is_mil: bool, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        font_family = "Helvetica Neue, Arial, DejaVu Sans, sans-serif"

        self.pos_label = QLabel(pos_name)
        self.pos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pos_label.setFont(QFont("sans-serif", 10, QFont.Weight.Bold))

        self.val_label = QLabel(value_text)
        self.val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.val_label.setFont(QFont("sans-serif", 12, QFont.Weight.Bold))

        layout.addWidget(self.pos_label)
        layout.addWidget(self.val_label)

        if is_mil:
            bg_color = "#FFE8D6"
            border_color = "#E35E28"
            text_color = "#A83E12"
        else:
            bg_color = "#EBF4F6"
            border_color = "#165E7D"
            text_color = "#165E7D"

        self.setStyleSheet(f"""
            ValueChip {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                background: transparent;
                font-family: {font_family};
            }}
        """)


class BreakdownPanel(QFrame):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.sound_player = SoundPlayer.get_instance()

        self.setStyleSheet("""
            BreakdownPanel {
                background-color: #F8F9FA;
                border: 2px solid #E0E3E8;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        # 1. Título y botón de pronunciación
        top_row = QHBoxLayout()
        title_label = QLabel("Valor Posicional y Descomposición")
        title_label.setFont(QFont("sans-serif", 13, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2D3748;")
        top_row.addWidget(title_label)

        top_row.addStretch()

        self.speak_btn = QPushButton("🔊 Escuchar cómo se lee")
        self.speak_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.speak_btn.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        self.speak_btn.setStyleSheet("""
            QPushButton {
                background-color: #165E7D;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #2080AA;
            }
            QPushButton:pressed {
                background-color: #0E4459;
            }
        """)
        self.speak_btn.clicked.connect(self._on_speak_clicked)
        top_row.addWidget(self.speak_btn)

        layout.addLayout(top_row)

        # 2. Número con signos de puntuación correctos y en palabras
        self.words_label = QLabel("")
        self.words_label.setWordWrap(True)
        self.words_label.setFont(QFont("sans-serif", 14, QFont.Weight.DemiBold))
        self.words_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #1A202C;
            border: 1px solid #CBD5E0;
            border-radius: 8px;
            padding: 10px 14px;
        """)
        layout.addWidget(self.words_label)

        # 3. Fichas de descomposición aditiva (sin ceros innecesarios)
        self.chips_container = QWidget()
        self.chips_layout = QHBoxLayout(self.chips_container)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(8)
        layout.addWidget(self.chips_container)

        # 4. Mensaje pedagógico interactivo de transformaciones y acarreos
        self.pedagogy_banner = QLabel("¡Usa las flechas ▲ y ▼ para ver cómo cambian los valores!")
        self.pedagogy_banner.setFont(QFont("sans-serif", 11))
        self.pedagogy_banner.setStyleSheet("""
            background-color: #FEFCBF;
            color: #744210;
            border: 1px solid #ECC94B;
            border-radius: 6px;
            padding: 8px 12px;
        """)
        layout.addWidget(self.pedagogy_banner)

        self.model.valueChanged.connect(self.update_display)
        self.model.carryEvent.connect(self._on_carry_event)

        self.update_display(self.model.value, self.model.get_digits(), {})

    def update_display(self, new_val: int, digits: list[int], info: dict):
        words = numero_a_palabras(new_val)
        # Signos de puntuación correctos con punto de miles
        formatted_num = formatear_cifra_es(new_val)
        self.words_label.setText(f"<b>{formatted_num}</b>  —  « {words} »")

        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        # Descomposición aditiva: omitir ceros (desaparecen los spots con cero)
        decomp = descomposicion_aditiva(new_val, self.model.active_digits, omit_zeros=True)
        for i, item in enumerate(decomp):
            chip = ValueChip(
                pos_name=item["pos"],
                value_text=item["text"],
                is_mil=item["is_mil"]
            )
            self.chips_layout.addWidget(chip)

            if i < len(decomp) - 1:
                plus_label = QLabel("+")
                plus_label.setFont(QFont("sans-serif", 14, QFont.Weight.Bold))
                plus_label.setStyleSheet("color: #718096;")
                self.chips_layout.addWidget(plus_label)

    def _on_carry_event(self, message: str, source_col: int):
        self.pedagogy_banner.setText(f"★ {message}")
        self.pedagogy_banner.setStyleSheet("""
            background-color: #C6F6D5;
            color: #22543D;
            border: 1px solid #38A169;
            border-radius: 6px;
            padding: 8px 12px;
            font-weight: bold;
        """)

    def _on_speak_clicked(self):
        words = numero_a_palabras(self.model.value)
        self.sound_player.speak_text(words)
