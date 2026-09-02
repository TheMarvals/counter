"""
Módulo para convertir números a palabras en español e inglés,
con descomposición aditiva y formateo de signos de puntuación según el idioma.
- Español: punto de miles (103.245)
- Inglés: coma de miles (103,245)
"""

# ======================= ESPAÑOL =======================
UNIDADES_ES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
ESPECIALES_10_ES = [
    "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve"
]
DECENAS_ES = [
    "", "", "veinte", "treinta", "cuarenta", "cincuenta",
    "sesenta", "setenta", "ochenta", "noventa"
]
VEINTES_ES = [
    "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro",
    "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"
]
CENTENAS_ES = [
    "", "ciento", "doscientos", "trescientos", "cuatrocientos",
    "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"
]

# ======================= INGLÉS =======================
UNITS_EN = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS_EN = [
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen"
]
TENS_EN = [
    "", "", "twenty", "thirty", "forty", "fifty",
    "sixty", "seventy", "eighty", "ninety"
]


def formatear_cifra(n: int, lang: str = "es") -> str:
    """Formatea la cifra según el idioma: 103.245 en español o 103,245 en inglés."""
    if lang == "en":
        return f"{n:,}"
    return f"{n:,}".replace(",", ".")


formatear_cifra_es = formatear_cifra


def _centenas_a_palabras_es(n: int) -> str:
    if n == 0:
        return ""
    if n == 100:
        return "cien"

    partes = []
    c = n // 100
    resto = n % 100

    if c > 0:
        partes.append(CENTENAS_ES[c])

    if resto == 0:
        return " ".join(partes)

    if resto < 10:
        partes.append(UNIDADES_ES[resto])
    elif resto < 20:
        partes.append(ESPECIALES_10_ES[resto - 10])
    elif resto < 30:
        partes.append(VEINTES_ES[resto - 20])
    else:
        d = resto // 10
        u = resto % 10
        if u == 0:
            partes.append(DECENAS_ES[d])
        else:
            partes.append(f"{DECENAS_ES[d]} y {UNIDADES_ES[u]}")

    return " ".join(partes)


def _hundreds_to_words_en(n: int) -> str:
    if n == 0:
        return ""

    partes = []
    c = n // 100
    resto = n % 100

    if c > 0:
        partes.append(f"{UNITS_EN[c]} hundred")

    if resto == 0:
        return " ".join(partes)

    if resto < 10:
        partes.append(UNITS_EN[resto])
    elif resto < 20:
        partes.append(TEENS_EN[resto - 10])
    else:
        d = resto // 10
        u = resto % 10
        if u == 0:
            partes.append(TENS_EN[d])
        else:
            partes.append(f"{TENS_EN[d]}-{UNITS_EN[u]}")

    return " ".join(partes)


def numero_a_palabras(n: int, lang: str = "es") -> str:
    """Convierte un número a palabras en español o inglés."""
    if lang == "en":
        if n == 0:
            return "Zero"
        miles = n // 1000
        units = n % 1000
        partes = []
        if miles > 0:
            partes.append(f"{_hundreds_to_words_en(miles)} thousand")
        if units > 0:
            partes.append(_hundreds_to_words_en(units))
        res = " ".join(partes).strip()
        return res.capitalize()

    # Español
    if n == 0:
        return "Cero"

    miles = n // 1000
    unidades = n % 1000

    partes = []
    if miles > 0:
        if miles == 1:
            partes.append("mil")
        else:
            texto_miles = _centenas_a_palabras_es(miles)
            if texto_miles.endswith("veintiuno"):
                texto_miles = texto_miles[:-3] + "ún"
            elif texto_miles.endswith(" uno"):
                texto_miles = texto_miles[:-4] + " un"
            partes.append(f"{texto_miles} mil")

    if unidades > 0:
        partes.append(_centenas_a_palabras_es(unidades))

    resultado = " ".join(partes).strip()
    return resultado.capitalize()


def descomposicion_aditiva(n: int, active_digits: int = 6, omit_zeros: bool = True, lang: str = "es") -> list[dict]:
    """Retorna la descomposición aditiva adaptada al idioma."""
    if lang == "en":
        pos_names = ["HTh", "TTh", "Th", "H", "T", "O"]
    else:
        pos_names = ["CM", "DM", "UM", "C", "D", "U"]

    weights = [100000, 10000, 1000, 100, 10, 1]
    is_mil_flags = [True, True, True, False, False, False]

    if n == 0:
        return [{
            "pos": pos_names[-1],
            "digit": 0,
            "value": 0,
            "text": "0",
            "is_mil": False
        }]

    start_idx = 6 - active_digits
    res = []
    for i in range(start_idx, 6):
        w = weights[i]
        d = (n // w) % 10
        val = d * w
        if omit_zeros and val == 0:
            continue
        formatted_val = formatear_cifra(val, lang=lang)
        res.append({
            "pos": pos_names[i],
            "digit": d,
            "value": val,
            "text": formatted_val,
            "is_mil": is_mil_flags[i]
        })
    return res
