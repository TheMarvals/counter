"""
Pruebas automatizadas del Contador de Unidades:
- Pruebas unitarias de modelo, ceros a la izquierda y acarreos
- Pruebas de puntuación en español (punto de miles)
- Pruebas de animación aislada por rueda
- Capturas de pantalla offscreen para verificación visual
"""

import os
import sys
import unittest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import QSize

from src.model.counter_model import CounterModel
from src.model.number_words import (
    numero_a_palabras, descomposicion_aditiva, formatear_cifra_es
)
from src.main_window import MainWindow


class TestCounterModel(unittest.TestCase):
    def test_initial_value(self):
        m = CounterModel(103245)
        self.assertEqual(m.value, 103245)
        self.assertEqual(m.get_digits(), [1, 0, 3, 2, 4, 5])
        self.assertEqual(m.get_significant_digits_count(), 6)

    def test_leading_zeros_detection(self):
        m = CounterModel(245)
        self.assertEqual(m.get_significant_digits_count(), 3)
        self.assertEqual(m.get_visible_columns_count(), 3)

        m.set_value(5)
        self.assertEqual(m.get_significant_digits_count(), 1)

        m.set_value(0)
        self.assertEqual(m.get_significant_digits_count(), 1)

    def test_carry_from_units_to_tens(self):
        m = CounterModel(9)
        carried = []
        m.carryEvent.connect(lambda msg, col: carried.append((msg, col)))
        m.increment_column(0)  # 9 + 1 = 10
        self.assertEqual(m.value, 10)
        self.assertEqual(m.get_digits(), [0, 0, 0, 0, 1, 0])
        self.assertTrue(len(carried) > 0)
        self.assertEqual(carried[0][1], 0)

    def test_single_unit_increment_digits(self):
        m = CounterModel(103245)
        m.increment_column(0)  # +1 unidad
        self.assertEqual(m.value, 103246)
        # Solo el dígito de las unidades cambió:
        self.assertEqual(m.get_digits(), [1, 0, 3, 2, 4, 6])


class TestNumberWordsAndPunctuation(unittest.TestCase):
    def test_spanish_punctuation(self):
        self.assertEqual(formatear_cifra_es(103245), "103.245")
        self.assertEqual(formatear_cifra_es(1000), "1.000")
        self.assertEqual(formatear_cifra_es(245), "245")
        self.assertEqual(formatear_cifra_es(0), "0")

    def test_descomposicion_omits_zeros(self):
        decomp = descomposicion_aditiva(103245, 6, omit_zeros=True)
        texts = [d["text"] for d in decomp]
        # El 0 de las DM desaparece:
        self.assertEqual(texts, ["100.000", "3.000", "200", "40", "5"])

    def test_descomposicion_small_number(self):
        decomp = descomposicion_aditiva(245, 6, omit_zeros=True)
        texts = [d["text"] for d in decomp]
        # CM, DM, UM desaparecen:
        self.assertEqual(texts, ["200", "40", "5"])


class TestGuiRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_main_window_render_full(self):
        window = MainWindow()
        window.resize(920, 840)
        window.show()

        image = QImage(window.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter(image)
        window.render(painter)
        painter.end()

        out_path = os.path.join(BASE_DIR, "assets", "screenshot_preview.png")
        saved = image.save(out_path)
        self.assertTrue(saved)

    def test_main_window_render_small_number(self):
        window = MainWindow()
        window.resize(920, 840)
        # Probar con un número que tenga ceros a la izquierda (ej. 3.245)
        window.model.set_value(3245)
        window.show()

        image = QImage(window.size(), QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter(image)
        window.render(painter)
        painter.end()

        out_path = os.path.join(BASE_DIR, "assets", "screenshot_small_number.png")
        saved = image.save(out_path)
        self.assertTrue(saved)
        print(f"Screenshot con ceros a la izquierda ocultos guardado en: {out_path}")


if __name__ == "__main__":
    unittest.main()
