"""Normalización de unidades y de números escritos al estilo colombiano.

Reglas (ver documento de diseño, sección 2):
* La unidad original se conserva siempre; aquí solo se calcula el valor canónico.
* 1 PS (CV métrico) = 0,98632 hp. Las marcas usan hp, PS, CV o kW a conveniencia.
* Un dato que no se puede interpretar devuelve None: nunca 0 ni un valor inventado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Factores hacia la unidad canónica de cada magnitud.
_POTENCIA_A_HP = {
    "hp": 1.0,
    "bhp": 1.0,
    "ps": 0.98632,
    "cv": 0.98632,
    "kw": 1.34102,
}
_TORQUE_A_NM = {
    "nm": 1.0,
    "n·m": 1.0,
    "n.m": 1.0,
    "kgf·m": 9.80665,
    "kgfm": 9.80665,
    "kgm": 9.80665,
    "kgf.m": 9.80665,
    "lb·ft": 1.35582,
    "lbft": 1.35582,
    "lb-ft": 1.35582,
}
LITROS_POR_GALON_US = 3.785411784

_NUM = r"\d{1,3}(?:[.\s]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?"


def parse_numero(texto: str) -> float | None:
    """Convierte '17,2', '8.500', '1.234,5' o '17.2' en float.

    Heurística colombiana: la coma es decimal; el punto es separador de miles cuando
    lo siguen exactamente 3 dígitos (8.500). '17.2' se lee como decimal.
    """
    if texto is None:
        return None
    t = texto.strip().replace(" ", " ")
    m = re.search(_NUM, t)
    if not m:
        return None
    s = m.group(0).replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


@dataclass(frozen=True)
class ValorConRpm:
    valor: float
    unidad_original: str
    a_rpm: int | None


def _parse_con_rpm(texto: str, tabla: dict[str, float]) -> tuple[ValorConRpm, float] | None:
    t = texto.lower().replace(" ", " ")
    unidades = sorted(tabla, key=len, reverse=True)
    patron_u = "|".join(re.escape(u) for u in unidades)
    m = re.search(rf"({_NUM})\s*({patron_u})\b", t)
    if not m:
        return None
    valor = parse_numero(m.group(1))
    if valor is None:
        return None
    unidad = m.group(2)
    rpm = None
    resto = t[m.end():]
    mr = re.search(rf"(?:@|a|/|,)?\s*({_NUM})\s*(?:rpm|r/min|min-1)", resto)
    if mr:
        r = parse_numero(mr.group(1))
        rpm = int(r) if r is not None else None
    return ValorConRpm(valor, unidad, rpm), tabla[unidad]


def potencia_a_hp(texto: str) -> tuple[float, ValorConRpm] | None:
    """'15,4 PS @ 8.500 rpm' -> (15.19, ValorConRpm(15.4, 'ps', 8500))."""
    r = _parse_con_rpm(texto, _POTENCIA_A_HP)
    if r is None:
        return None
    v, factor = r
    return round(v.valor * factor, 2), v


def torque_a_nm(texto: str) -> tuple[float, ValorConRpm] | None:
    """'1,4 kgf·m @ 7.000 rpm' -> (13.73, ...)."""
    r = _parse_con_rpm(texto, _TORQUE_A_NM)
    if r is None:
        return None
    v, factor = r
    return round(v.valor * factor, 2), v


def consumo_a_km_gal(texto: str) -> float | None:
    """Acepta km/gal o km/l. Devuelve km por galón US."""
    t = texto.lower()
    v = parse_numero(t)
    if v is None:
        return None
    if re.search(r"km\s*/\s*(?:l\b|lt|litro)", t):
        return round(v * LITROS_POR_GALON_US, 1)
    if re.search(r"km\s*/\s*gal", t):
        return v
    return None  # unidad desconocida: no adivinar


def longitud_a_mm(texto: str) -> float | None:
    t = texto.lower()
    v = parse_numero(t)
    if v is None:
        return None
    if re.search(r"(?<![a-z])mm\b", t):
        return v
    if re.search(r"(?<![a-z])cm\b", t):
        return v * 10
    if re.search(r"\bm\b", t) and v < 5:
        return v * 1000
    return None


def volumen_a_litros(texto: str) -> float | None:
    """'12 L / 3.17 Gal' -> 12; '3,4 Galones (13 Lt)' -> 13; '3,4 galones' -> 12.87.

    Prefiere el número que va seguido de litros; si solo hay galones, convierte (galón US).
    Sin unidad reconocible devuelve None para no confundir galones con litros.
    """
    t = texto.lower()
    m = re.search(rf"({_NUM})\s*(?:l\b|lt|litro)", t)
    if m:
        return parse_numero(m.group(1))
    m = re.search(rf"({_NUM})\s*gal", t)
    if m:
        v = parse_numero(m.group(1))
        return round(v * LITROS_POR_GALON_US, 2) if v is not None else None
    return None
