"""
Panel de retos y misiones pedagógicas para niños:
Plantea desafíos interactivos de formación de números, sumas de valor posicional
y reconocimiento de dígitos. Premia con estrellas y sonidos festivos.
"""

import random
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)

from src.audio.sound_player import SoundPlayer


class ChallengePanel(QFrame):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.sound_player = SoundPlayer.get_instance()

        self.score = 0
        self.stars = 0
        self.current_challenge = None

        self.setStyleSheet("""
            ChallengePanel {
                background-color: #FFFDF5;
                border: 2px solid #F6E05E;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Barra superior
        header = QHBoxLayout()
        title = QLabel("Desafíos y Misiones")
        title.setFont(QFont("DejaVu Sans", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #744210;")
        header.addWidget(title)

        header.addStretch()

        self.stars_label = QLabel("★ 0 Estrellas")
        self.stars_label.setFont(QFont("DejaVu Sans", 11, QFont.Weight.Bold))
        self.stars_label.setStyleSheet("color: #D69E2E;")
        header.addWidget(self.stars_label)

        layout.addLayout(header)

        # Enunciado del reto
        self.prompt_label = QLabel("Pulsa 'Nuevo Desafío' para comenzar a jugar.")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setFont(QFont("DejaVu Sans", 12, QFont.Weight.Bold))
        self.prompt_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #2D3748;
            border: 2px dashed #CBD5E0;
            border-radius: 8px;
            padding: 10px 14px;
        """)
        layout.addWidget(self.prompt_label)

        # Botonera de acciones
        actions = QHBoxLayout()
        self.new_challenge_btn = QPushButton("Nuevo Desafío")
        self.new_challenge_btn.setFont(QFont("DejaVu Sans", 10, QFont.Weight.Bold))
        self.new_challenge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_challenge_btn.setStyleSheet("""
            QPushButton {
                background-color: #ED8936;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 14px;
            }
            QPushButton:hover { background-color: #DD6B20; }
        """)
        self.new_challenge_btn.clicked.connect(self.generate_new_challenge)
        actions.addWidget(self.new_challenge_btn)

        self.check_btn = QPushButton("Comprobar")
        self.check_btn.setFont(QFont("DejaVu Sans", 10, QFont.Weight.Bold))
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #38A169;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 16px;
            }
            QPushButton:hover { background-color: #2F855A; }
        """)
        self.check_btn.clicked.connect(self.verify_challenge)
        actions.addWidget(self.check_btn)

        actions.addStretch()

        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("DejaVu Sans", 11, QFont.Weight.Bold))
        actions.addWidget(self.feedback_label)

        layout.addLayout(actions)

        self.model.valueChanged.connect(self._on_model_changed)

    def generate_new_challenge(self):
        active_digits = self.model.active_digits
        challenge_type = random.choice(["form_number", "change_digit", "add_units"])

        if challenge_type == "form_number":
            min_v = 10 ** (active_digits - 1) if active_digits > 1 else 0
            max_v = (10 ** active_digits) - 1
            target = random.randint(min_v, max_v)
            formatted_target = f"{target:,}".replace(",", ".")
            self.current_challenge = {
                "type": "target_value",
                "target": target,
                "text": f"Misión: ¡Gira las ruedas hasta formar el número <b>{formatted_target}</b>!"
            }

        elif challenge_type == "change_digit":
            col_options = ["U", "D", "C", "UM", "DM", "CM"][:active_digits]
            col_names = ["Unidades", "Decenas", "Centenas", "Unidades de Mil", "Decenas de Mil", "Centenas de Mil"][:active_digits]
            idx = random.randint(0, active_digits - 1)
            target_digit = random.randint(1, 9)
            self.current_challenge = {
                "type": "target_digit",
                "pos_idx": idx,
                "target_digit": target_digit,
                "text": f"Misión: Haz que la cifra de las <b>{col_names[idx]} ({col_options[idx]})</b> sea igual a <b>{target_digit}</b>."
            }

        else:
            col_options = ["U", "D", "C", "UM"][:min(4, active_digits)]
            col_names = ["unidades", "decenas", "centenas", "unidades de mil"][:min(4, active_digits)]
            idx = random.randint(0, len(col_options) - 1)
            amount = random.randint(1, 3)
            current_val = self.model.value
            target = current_val + amount * (10 ** idx)
            formatted_target = f"{target:,}".replace(",", ".")
            self.current_challenge = {
                "type": "target_value",
                "target": target,
                "text": f"Misión: Al número actual, ¡suma <b>{amount} {col_names[idx]}</b>!"
            }

        self.prompt_label.setText(self.current_challenge["text"])
        self.feedback_label.setText("")

    def _on_model_changed(self, new_val, digits, info):
        if self.current_challenge:
            if self._is_solved():
                self._handle_success()

    def _is_solved(self) -> bool:
        if not self.current_challenge:
            return False
        c_type = self.current_challenge["type"]
        if c_type == "target_value":
            return self.model.value == self.current_challenge["target"]
        elif c_type == "target_digit":
            idx = self.current_challenge["pos_idx"]
            return self.model.get_digit_at_pos(idx) == self.current_challenge["target_digit"]
        return False

    def verify_challenge(self):
        if not self.current_challenge:
            self.generate_new_challenge()
            return

        if self._is_solved():
            self._handle_success()
        else:
            self.feedback_label.setText("Casi... ¡Sigue probando!")
            self.feedback_label.setStyleSheet("color: #C53030;")

    def _handle_success(self):
        self.stars += 1
        self.stars_label.setText(f"★ {self.stars} {'Estrellas' if self.stars != 1 else 'Estrella'}")
        self.feedback_label.setText("¡EXCELENTE! ¡Completado con éxito!")
        self.feedback_label.setStyleSheet("color: #2F855A;")
        self.sound_player.play_chime()
        self.current_challenge = None
        QTimer.singleShot(2200, self.generate_new_challenge)
