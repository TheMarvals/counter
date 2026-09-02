"""
Modelo del contador numérico para niños.
Maneja el valor de 0 a 999.999 y las 6 unidades de posición:
CM (Centenas de Mil), DM (Decenas de Mil), UM (Unidades de Mil),
C (Centenas), D (Decenas), U (Unidades).
Soporta ocultar ceros a la izquierda y cálculo de dígitos significativos.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class CounterModel(QObject):
    valueChanged = pyqtSignal(int, list, dict)
    carryEvent = pyqtSignal(str, int)
    displayConfigChanged = pyqtSignal()

    COL_NAMES = ["U", "D", "C", "UM", "DM", "CM"]
    COL_FULL_NAMES = [
        "Unidades",
        "Decenas",
        "Centenas",
        "Unidades de Mil",
        "Decenas de Mil",
        "Centenas de Mil"
    ]
    COL_WEIGHTS = [1, 10, 100, 1000, 10000, 100000]

    def __init__(self, initial_value: int = 103245, max_digits: int = 6):
        super().__init__()
        self._max_digits = max_digits
        self._max_val = 10 ** max_digits - 1
        self._value = max(0, min(self._max_val, initial_value))
        self._active_digits = max_digits
        self._hide_leading_zeros = True  # Ocultar ceros a la izquierda por defecto

    @property
    def value(self) -> int:
        return self._value

    @property
    def active_digits(self) -> int:
        return self._active_digits

    @active_digits.setter
    def active_digits(self, count: int):
        self._active_digits = max(1, min(6, count))
        self._max_val = 10 ** self._active_digits - 1
        if self._value > self._max_val:
            self.set_value(self._max_val)
        else:
            self._notify_change(reason="active_digits_changed")
        self.displayConfigChanged.emit()

    @property
    def hide_leading_zeros(self) -> bool:
        return self._hide_leading_zeros

    @hide_leading_zeros.setter
    def hide_leading_zeros(self, val: bool):
        if self._hide_leading_zeros != val:
            self._hide_leading_zeros = val
            self._notify_change(reason="leading_zeros_toggled")
            self.displayConfigChanged.emit()

    def get_significant_digits_count(self) -> int:
        """Retorna la cantidad de cifras significativas (mínimo 1 para el 0)."""
        if self._value == 0:
            return 1
        return len(str(self._value))

    def get_visible_columns_count(self) -> int:
        """Calcula cuántas columnas deben mostrarse según la configuración."""
        if not self._hide_leading_zeros:
            return self._active_digits
        return max(1, min(self._active_digits, self.get_significant_digits_count()))

    def is_column_visible(self, pos_idx: int) -> bool:
        """
        Indica si la columna (0=U, 1=D, 2=C, 3=UM, 4=DM, 5=CM) debe estar visible.
        """
        vis_count = self.get_visible_columns_count()
        return pos_idx < vis_count

    def activate_next_column(self):
        """Añade 1 unidad a la columna inmediatamente superior a la visible actual."""
        vis_count = self.get_visible_columns_count()
        if vis_count < self._active_digits:
            next_idx = vis_count
            self.increment_column(next_idx)

    def set_value(self, val: int, reason: str = "direct"):
        val = max(0, min(self._max_val, val))
        old_val = self._value
        if old_val != val:
            self._value = val
            self._notify_change(old_val=old_val, reason=reason)

    def get_digits(self) -> list[int]:
        s = f"{self._value:06d}"
        return [int(ch) for ch in s]

    def get_digit_at_pos(self, pos_idx: int) -> int:
        return (self._value // (10 ** pos_idx)) % 10

    def increment_column(self, pos_idx: int):
        weight = self.COL_WEIGHTS[pos_idx]
        old_val = self._value
        new_val = old_val + weight
        if new_val > self._max_val:
            new_val = new_val % (self._max_val + 1)

        curr_digit = self.get_digit_at_pos(pos_idx)
        if curr_digit == 9:
            dest_col = min(5, pos_idx + 1)
            msg = f"¡10 {self.COL_FULL_NAMES[pos_idx]} se convierten en 1 {self.COL_FULL_NAMES[dest_col]}!"
            self.carryEvent.emit(msg, pos_idx)

        self._value = new_val
        self._notify_change(old_val=old_val, reason=f"inc_{self.COL_NAMES[pos_idx]}")

    def decrement_column(self, pos_idx: int):
        weight = self.COL_WEIGHTS[pos_idx]
        old_val = self._value
        new_val = old_val - weight
        if new_val < 0:
            new_val = self._max_val - (abs(new_val) - 1)

        curr_digit = self.get_digit_at_pos(pos_idx)
        if curr_digit == 0:
            dest_col = min(5, pos_idx + 1)
            msg = f"¡Desagrupación! Se toma 1 {self.COL_FULL_NAMES[dest_col]} para obtener 10 {self.COL_FULL_NAMES[pos_idx]}."
            self.carryEvent.emit(msg, pos_idx)

        self._value = new_val
        self._notify_change(old_val=old_val, reason=f"dec_{self.COL_NAMES[pos_idx]}")

    def reset(self):
        self.set_value(0, reason="reset")

    def _notify_change(self, old_val: int = None, reason: str = "change"):
        digits = self.get_digits()
        info = {
            "old_value": old_val if old_val is not None else self._value,
            "new_value": self._value,
            "reason": reason,
            "active_digits": self._active_digits,
            "significant_digits": self.get_significant_digits_count(),
            "visible_columns": self.get_visible_columns_count()
        }
        self.valueChanged.emit(self._value, digits, info)
