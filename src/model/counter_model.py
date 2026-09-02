"""
Modelo del contador numérico para niños.
Maneja el valor de 0 a 999.999 y las 6 unidades de posición.
Soporta:
- Modo Automático (acarreos automáticos) y Modo Manual (el niño mueve cada posición por sí mismo).
- Bilingüe (Español e Inglés).
- Ocultación de ceros a la izquierda.
"""

from PyQt6.QtCore import QObject, pyqtSignal


class CounterModel(QObject):
    valueChanged = pyqtSignal(int, list, dict)
    carryEvent = pyqtSignal(str, int)
    displayConfigChanged = pyqtSignal()

    NAMES_ES = ["U", "D", "C", "UM", "DM", "CM"]
    FULL_NAMES_ES = [
        "Unidades", "Decenas", "Centenas",
        "Unidades de Mil", "Decenas de Mil", "Centenas de Mil"
    ]

    NAMES_EN = ["O", "T", "H", "Th", "TTh", "HTh"]
    FULL_NAMES_EN = [
        "Ones", "Tens", "Hundreds",
        "Thousands", "Ten Thousands", "Hundred Thousands"
    ]

    COL_WEIGHTS = [1, 10, 100, 1000, 10000, 100000]

    def __init__(self, initial_value: int = 103245, max_digits: int = 6):
        super().__init__()
        self._max_digits = max_digits
        self._max_val = 10 ** max_digits - 1
        self._value = max(0, min(self._max_val, initial_value))
        self._active_digits = max_digits
        self._hide_leading_zeros = True
        self._mode = "auto"   # "auto" o "manual"
        self._lang = "es"     # "es" o "en"

    @property
    def value(self) -> int:
        return self._value

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, new_mode: str):
        if new_mode in ["auto", "manual"] and self._mode != new_mode:
            self._mode = new_mode
            self.displayConfigChanged.emit()

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, new_lang: str):
        if new_lang in ["es", "en"] and self._lang != new_lang:
            self._lang = new_lang
            self.displayConfigChanged.emit()
            self._notify_change(reason="lang_changed")

    @property
    def col_names(self) -> list[str]:
        return self.NAMES_EN if self._lang == "en" else self.NAMES_ES

    @property
    def col_full_names(self) -> list[str]:
        return self.FULL_NAMES_EN if self._lang == "en" else self.FULL_NAMES_ES

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
        if self._value == 0:
            return 1
        return len(str(self._value))

    def get_visible_columns_count(self) -> int:
        if not self._hide_leading_zeros:
            return self._active_digits
        return max(1, min(self._active_digits, self.get_significant_digits_count()))

    def is_column_visible(self, pos_idx: int) -> bool:
        vis_count = self.get_visible_columns_count()
        return pos_idx < vis_count

    def activate_next_column(self):
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
        curr_digit = self.get_digit_at_pos(pos_idx)

        # MODO MANUAL: Únicamente gira el dígito actual (0..9) de forma independiente
        if self._mode == "manual":
            next_digit = (curr_digit + 1) % 10
            diff = (next_digit - curr_digit) * weight
            new_val = old_val + diff

            if curr_digit == 9:
                dest_col = min(5, pos_idx + 1)
                dest_name = self.col_full_names[dest_col]
                curr_name = self.col_full_names[pos_idx]
                if self._lang == "en":
                    msg = f"Completed 10 {curr_name}! In Manual Mode, remember to add 1 to the {dest_name} yourself."
                else:
                    msg = f"¡Completaste 10 {curr_name}! En modo manual, recuerda sumar 1 en {dest_name}."
                self.carryEvent.emit(msg, pos_idx)

            self._value = new_val
            self._notify_change(old_val=old_val, reason=f"manual_inc_{pos_idx}")
            return

        # MODO AUTOMÁTICO: Acarreo en cascada normal
        new_val = old_val + weight
        if new_val > self._max_val:
            new_val = new_val % (self._max_val + 1)

        if curr_digit == 9:
            dest_col = min(5, pos_idx + 1)
            dest_name = self.col_full_names[dest_col]
            curr_name = self.col_full_names[pos_idx]
            if self._lang == "en":
                msg = f"10 {curr_name} become 1 {dest_name}!"
            else:
                msg = f"¡10 {curr_name} se convierten en 1 {dest_name}!"
            self.carryEvent.emit(msg, pos_idx)

        self._value = new_val
        self._notify_change(old_val=old_val, reason=f"inc_{pos_idx}")

    def decrement_column(self, pos_idx: int):
        weight = self.COL_WEIGHTS[pos_idx]
        old_val = self._value
        curr_digit = self.get_digit_at_pos(pos_idx)

        # MODO MANUAL: Desagrupación manual independiente
        if self._mode == "manual":
            next_digit = (curr_digit - 1) % 10
            diff = (next_digit - curr_digit) * weight
            new_val = old_val + diff

            if curr_digit == 0:
                dest_col = min(5, pos_idx + 1)
                dest_name = self.col_full_names[dest_col]
                curr_name = self.col_full_names[pos_idx]
                if self._lang == "en":
                    msg = f"Manual regrouping! In Manual Mode, remember to subtract 1 from {dest_name}."
                else:
                    msg = f"¡Desagrupación manual! En modo manual, recuerda restar 1 a {dest_name}."
                self.carryEvent.emit(msg, pos_idx)

            self._value = new_val
            self._notify_change(old_val=old_val, reason=f"manual_dec_{pos_idx}")
            return

        # MODO AUTOMÁTICO
        new_val = old_val - weight
        if new_val < 0:
            new_val = self._max_val - (abs(new_val) - 1)

        if curr_digit == 0:
            dest_col = min(5, pos_idx + 1)
            dest_name = self.col_full_names[dest_col]
            curr_name = self.col_full_names[pos_idx]
            if self._lang == "en":
                msg = f"Regrouping! 1 {dest_name} is traded for 10 {curr_name}."
            else:
                msg = f"¡Desagrupación! Se toma 1 {dest_name} para obtener 10 {curr_name}."
            self.carryEvent.emit(msg, pos_idx)

        self._value = new_val
        self._notify_change(old_val=old_val, reason=f"dec_{pos_idx}")

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
            "visible_columns": self.get_visible_columns_count(),
            "mode": self._mode,
            "lang": self._lang
        }
        self.valueChanged.emit(self._value, digits, info)
