"""
Ventana Principal de la Aplicación del Contador para Niños.
Multiplataforma (Linux / macOS / Windows).
Soporta:
- Modo Automático y Modo Manual pedagógico.
- Idiomas: Español e Inglés.
- Ceros a la izquierda ocultos.
"""

import random
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QFrame, QButtonGroup
)

from src.model.counter_model import CounterModel
from src.widgets.odometer_display import OdometerDisplay
from src.widgets.breakdown_panel import BreakdownPanel
from src.widgets.challenge_panel import ChallengePanel
from src.audio.sound_player import SoundPlayer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(960, 880)
        self.setMinimumSize(840, 740)

        self.model = CounterModel(initial_value=103245, max_digits=6)
        self.sound_player = SoundPlayer.get_instance()

        self.setStyleSheet("""
            QMainWindow {
                background-color: #F0F4F8;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # 1. Barra superior
        top_bar = self._create_top_bar()
        main_layout.addWidget(top_bar)

        # 2. Área desplazable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(8, 6, 8, 10)
        scroll_layout.setSpacing(16)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.odometer = OdometerDisplay(self.model)
        scroll_layout.addWidget(self.odometer, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.breakdown_panel = BreakdownPanel(self.model)
        scroll_layout.addWidget(self.breakdown_panel)

        self.challenge_panel = ChallengePanel(self.model)
        scroll_layout.addWidget(self.challenge_panel)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        self.model.displayConfigChanged.connect(self._on_display_config_changed)
        self._update_ui_texts()

    def _create_top_bar(self) -> QWidget:
        bar = QFrame()
        bar.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #D2D6DC;
                border-radius: 10px;
                padding: 4px;
            }
            QPushButton {
                font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "Arial", "DejaVu Sans", sans-serif;
                font-weight: bold;
                font-size: 11px;
                border-radius: 6px;
                padding: 6px 12px;
            }
        """)
        layout = QVBoxLayout(bar)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Fila 1: Nivel, Modo (Auto/Manual) e Idioma (ES/EN)
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        self.lvl_label = QLabel("Nivel:")
        self.lvl_label.setFont(QFont("sans-serif", 11, QFont.Weight.Bold))
        self.lvl_label.setStyleSheet("color: #4A5568;")
        row1.addWidget(self.lvl_label)

        self.btn_lvl3 = QPushButton("3 Dígitos")
        self.btn_lvl4 = QPushButton("4 Dígitos")
        self.btn_lvl6 = QPushButton("6 Dígitos")

        for btn in [self.btn_lvl3, self.btn_lvl4, self.btn_lvl6]:
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_lvl6.setChecked(True)

        self.lvl_group = QButtonGroup(self)
        self.lvl_group.addButton(self.btn_lvl3, 3)
        self.lvl_group.addButton(self.btn_lvl4, 4)
        self.lvl_group.addButton(self.btn_lvl6, 6)
        self.lvl_group.idClicked.connect(self._on_level_changed)

        for btn in [self.btn_lvl3, self.btn_lvl4, self.btn_lvl6]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #EDF2F7;
                    color: #4A5568;
                    border: 1px solid #CBD5E0;
                }
                QPushButton:checked {
                    background-color: #165E7D;
                    color: #FFFFFF;
                    border: 1px solid #0E4459;
                }
            """)
            row1.addWidget(btn)

        self.btn_add_col = QPushButton("+ Columna")
        self.btn_add_col.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_col.setStyleSheet("""
            QPushButton {
                background-color: #EBF8FF;
                color: #2B6CB0;
                border: 1px dashed #63B3ED;
            }
            QPushButton:hover { background-color: #BEE3F8; }
        """)
        self.btn_add_col.clicked.connect(self._on_add_col_clicked)
        row1.addWidget(self.btn_add_col)

        row1.addStretch()

        # Botón Modo Auto / Manual
        self.btn_mode = QPushButton("Modo: Automático")
        self.btn_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mode.setStyleSheet("""
            QPushButton {
                background-color: #EDF2F7;
                color: #2D3748;
                border: 1px solid #CBD5E0;
            }
            QPushButton:hover { background-color: #E2E8F0; }
        """)
        self.btn_mode.clicked.connect(self._on_toggle_mode)
        row1.addWidget(self.btn_mode)

        # Botón Idioma
        self.btn_lang = QPushButton("🌐 ES")
        self.btn_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_lang.setStyleSheet("""
            QPushButton {
                background-color: #FEFCBF;
                color: #744210;
                border: 1px solid #D69E2E;
            }
            QPushButton:hover { background-color: #FAF089; }
        """)
        self.btn_lang.clicked.connect(self._on_toggle_lang)
        row1.addWidget(self.btn_lang)

        layout.addLayout(row1)

        # Fila 2: Ceros a la izquierda, Sorpresa, Reset, Sonido y Retos
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        self.btn_zeros = QPushButton("Ceros Izq: Ocultos")
        self.btn_zeros.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_zeros.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #2D3748;
                border: 1px solid #CBD5E0;
            }
            QPushButton:hover { background-color: #CBD5E0; }
        """)
        self.btn_zeros.clicked.connect(self._on_toggle_zeros)
        row2.addWidget(self.btn_zeros)

        self.btn_random = QPushButton("Número Sorpresa")
        self.btn_random.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_random.setStyleSheet("""
            QPushButton {
                background-color: #FEFCBF;
                color: #744210;
                border: 1px solid #D69E2E;
            }
            QPushButton:hover { background-color: #FAF089; }
        """)
        self.btn_random.clicked.connect(self._on_random_clicked)
        row2.addWidget(self.btn_random)

        self.btn_reset = QPushButton("Poner a 0")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #FED7D7;
                color: #9B2C2C;
                border: 1px solid #FEB2B2;
            }
            QPushButton:hover { background-color: #FEB2B2; }
        """)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        row2.addWidget(self.btn_reset)

        row2.addStretch()

        self.btn_sound = QPushButton("Sonido: ON")
        self.btn_sound.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_sound.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                color: #2D3748;
                border: 1px solid #CBD5E0;
            }
            QPushButton:hover { background-color: #CBD5E0; }
        """)
        self.btn_sound.clicked.connect(self._on_sound_toggle)
        row2.addWidget(self.btn_sound)

        self.btn_challenges = QPushButton("Retos: ON")
        self.btn_challenges.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_challenges.setStyleSheet("""
            QPushButton {
                background-color: #EBF8FF;
                color: #2B6CB0;
                border: 1px solid #BEE3F8;
            }
            QPushButton:hover { background-color: #BEE3F8; }
        """)
        self.btn_challenges.clicked.connect(self._on_challenge_toggle)
        row2.addWidget(self.btn_challenges)

        layout.addLayout(row2)

        return bar

    def _on_display_config_changed(self):
        self._update_ui_texts()

    def _update_ui_texts(self):
        lang = self.model.lang
        mode = self.model.mode

        if lang == "en":
            self.setWindowTitle("Mechanical Counter — Understanding Place Value")
            self.lvl_label.setText("Level:")
            self.btn_lvl3.setText("3 Digits")
            self.btn_lvl4.setText("4 Digits")
            self.btn_lvl6.setText("6 Digits")
            self.btn_add_col.setText("+ Column")
            self.btn_lang.setText("🌐 EN (English)")
            self.btn_random.setText("Surprise Number")
            self.btn_reset.setText("Reset to 0")
            self.btn_sound.setText("Sound: OFF" if self.sound_player.muted else "Sound: ON")
            self.btn_challenges.setText("Challenges: ON" if self.challenge_panel.isVisible() else "Challenges: OFF")
            self.btn_zeros.setText("Leading Zeros: Hidden" if self.model.hide_leading_zeros else "Leading Zeros: Visible")
            if mode == "manual":
                self.btn_mode.setText("Mode: Manual (No auto-carry)")
                self.btn_mode.setStyleSheet("background-color: #FEEBC8; color: #7B341E; border: 1px solid #DD6B20;")
            else:
                self.btn_mode.setText("Mode: Automatic")
                self.btn_mode.setStyleSheet("background-color: #EDF2F7; color: #2D3748; border: 1px solid #CBD5E0;")
        else:
            self.setWindowTitle("Contador Mecánico — Aprendiendo el Valor Posicional")
            self.lvl_label.setText("Nivel:")
            self.btn_lvl3.setText("3 Dígitos")
            self.btn_lvl4.setText("4 Dígitos")
            self.btn_lvl6.setText("6 Dígitos")
            self.btn_add_col.setText("+ Columna")
            self.btn_lang.setText("🌐 ES (Español)")
            self.btn_random.setText("Número Sorpresa")
            self.btn_reset.setText("Poner a 0")
            self.btn_sound.setText("Sonido: OFF" if self.sound_player.muted else "Sonido: ON")
            self.btn_challenges.setText("Retos: ON" if self.challenge_panel.isVisible() else "Retos: OFF")
            self.btn_zeros.setText("Ceros Izq: Ocultos" if self.model.hide_leading_zeros else "Ceros Izq: Visibles")
            if mode == "manual":
                self.btn_mode.setText("Modo: Manual (Sin auto-suma)")
                self.btn_mode.setStyleSheet("background-color: #FEEBC8; color: #7B341E; border: 1px solid #DD6B20;")
            else:
                self.btn_mode.setText("Modo: Automático")
                self.btn_mode.setStyleSheet("background-color: #EDF2F7; color: #2D3748; border: 1px solid #CBD5E0;")

    def _on_level_changed(self, count: int):
        self.model.active_digits = count

    def _on_add_col_clicked(self):
        self.sound_player.play_click()
        self.model.activate_next_column()

    def _on_toggle_mode(self):
        self.sound_player.play_click()
        self.model.mode = "manual" if self.model.mode == "auto" else "auto"

    def _on_toggle_lang(self):
        self.sound_player.play_click()
        self.model.lang = "en" if self.model.lang == "es" else "es"

    def _on_toggle_zeros(self):
        self.model.hide_leading_zeros = not self.model.hide_leading_zeros

    def _on_reset_clicked(self):
        self.sound_player.play_click()
        self.model.reset()

    def _on_random_clicked(self):
        self.sound_player.play_click()
        active = self.model.active_digits
        max_val = 10 ** active - 1
        min_val = 10 ** (active - 1) if active > 1 else 0
        val = random.randint(min_val, max_val)
        self.model.set_value(val, reason="random")

    def _on_sound_toggle(self):
        self.sound_player.muted = not self.sound_player.muted
        self._update_ui_texts()

    def _on_challenge_toggle(self):
        vis = not self.challenge_panel.isVisible()
        self.challenge_panel.setVisible(vis)
        self._update_ui_texts()
