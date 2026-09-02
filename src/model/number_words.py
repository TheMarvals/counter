"""
Módulo para convertir números a palabras en español y descomposición aditiva.
Formatea las cifras con los signos de puntuación correctos en español (punto de miles).
Omite los ceros en la descomposición aditiva (incluyendo ceros a la izquierda).
"""

UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
ESPECIALES_10 = [
    "diez", "once", "doce", "trece", "catorce", "quince",
    "dieciséis", "diecisiete", "dieciocho", "diecinueve"
]
DECENAS = [
    "", "", "veinte", "treinta", "cuarenta", "cincuenta",
    "sesenta", "setenta", "ochenta", "noventa"
]
VEINTES = [
    "veinte", "veintiuno", "veintidós", "veintitrés", "veinticuatro",
    "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"
]
CENTENAS = [
    "", "ciento", "doscientos", "trescientos", "cuatrocientos",
    "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"
]


def formatear_cifra_es(n: int) -> str:
    """Formatea un entero con punto de miles como en español: 103.245"""
    return f"{n:,}".replace(",", ".")


def _centenas_a_palabras(n: int) -> str:
    if n == 0:
        return ""
    if n == 100:
        return "cien"

    partes = []
    c = n // 100
    resto = n % 100

    if c > 0:
        partes.append(CENTENAS[c])

    if resto == 0:
        return " ".join(partes)

    if resto < 10:
        partes.append(UNIDADES[resto])
    elif resto < 20:
        partes.append(ESPECIALES_10[resto - 10])
    elif resto < 30:
        partes.append(VEINTES[resto - 20])
    else:
        d = resto // 10
        u = resto % 10
        if u == 0:
            partes.append(DECENAS[d])
        else:
            partes.append(f"{DECENAS[d]} y {UNIDADES[u]}")

    return " ".join(partes)


def numero_a_palabras(n: int) -> str:
    if n == 0:
        return "Cero"

    miles = n // 1000
    unidades = n % 1000

    partes = []
    if miles > 0:
        if miles == 1:
            partes.append("mil")
        else:
            texto_miles = _centenas_a_palabras(miles)
            if texto_miles.endswith("veintiuno"):
                texto_miles = texto_miles[:-3] + "ún"
            elif texto_miles.endswith(" uno"):
                texto_miles = texto_miles[:-4] + " un"
            partes.append(f"{texto_miles} mil")

    if unidades > 0:
        partes.append(_centenas_a_palabras(unidades))

    resultado = " ".join(partes).strip()
    return resultado.capitalize()


def descomposicion_aditiva(n: int, active_digits: int = 6, omit_zeros: bool = True) -> list[dict]:
    """
    Retorna la descomposición aditiva en potencias de 10.
    Si omit_zeros=True, desaparecen los spots que tengan ceros (ceros a la izquierda
    y ceros intermedios sin valor aditivo).
    Si n == 0, retorna una sola ficha con '0' en las Unidades.
    """
    pos_names = ["CM", "DM", "UM", "C", "D", "U"]
    weights = [100000, 10000, 1000, 100, 10, 1]
    is_mil_flags = [True, True, True, False, False, False]

    if n == 0:
        return [{
            "pos": "U",
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
        formatted_val = formatear_cifra_es(val)
        res.append({
            "pos": pos_names[i],
            "digit": d,
            "value": val,
            "text": formatted_val,
            "is_mil": is_mil_flags[i]
        })
    return res
