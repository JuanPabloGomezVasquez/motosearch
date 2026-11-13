"""Catálogo de atributos (espejo de db/seed/0001_catalogos.sql; un test verifica que coincidan)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from . import units


@dataclass(frozen=True)
class Atributo:
    clave: str
    tipo: str  # numero | texto | booleano | enum
    unidad: str | None = None
    minimo: float | None = None
    maximo: float | None = None
    enum: tuple[str, ...] = ()
    parser: Callable[[str], float | None] | None = None
    con_rpm: bool = False


def _num(t: str) -> float | None:
    return units.parse_numero(t)


def _potencia(t: str) -> float | None:
    r = units.potencia_a_hp(t)
    return r[0] if r else None


def _torque(t: str) -> float | None:
    r = units.torque_a_nm(t)
    return r[0] if r else None


def _mm(t: str) -> float | None:
    return units.longitud_a_mm(t) if any(u in t.lower() for u in ("mm", "cm", " m")) else _num(t)


_A = [
    Atributo("cilindrada", "numero", "cc", 49, 1900, parser=_num),
    Atributo("potencia_max", "numero", "hp", 2, 220, parser=_potencia, con_rpm=True),
    Atributo("torque_max", "numero", "N·m", 3, 250, parser=_torque, con_rpm=True),
    Atributo("potencia_electrica", "numero", "kW", 0.25, 100, parser=_num),
    Atributo("cilindros", "numero", None, 1, 6, parser=_num),
    Atributo("tiempos", "enum", enum=("2T", "4T")),
    Atributo("refrigeracion", "enum", enum=("aire", "aceite", "aire-aceite", "liquida")),
    Atributo("alimentacion", "enum", enum=("carburador", "inyeccion")),
    Atributo("norma_emisiones", "enum", enum=("Euro 2", "Euro 3", "Euro 4", "Euro 5", "Euro 5+")),
    Atributo("arranque", "enum", enum=("electrico", "pedal", "electrico+pedal")),
    Atributo("transmision_tipo", "enum", enum=("manual", "semiautomatica", "cvt", "dct", "directa")),
    Atributo("marchas", "numero", None, 1, 7, parser=_num),
    Atributo("peso_seco", "numero", "kg", 60, 400, parser=_num),
    Atributo("peso_orden_marcha", "numero", "kg", 70, 450, parser=_num),
    Atributo("capacidad_tanque", "numero", "L", 3, 35, parser=units.volumen_a_litros),
    Atributo("altura_sillin", "numero", "mm", 600, 1000, parser=_mm),
    Atributo("distancia_ejes", "numero", "mm", 1000, 1800, parser=_mm),
    Atributo("distancia_piso", "numero", "mm", 90, 350, parser=_mm),
    Atributo("freno_delantero", "enum", enum=("tambor", "disco", "doble disco")),
    Atributo("freno_trasero", "enum", enum=("tambor", "disco")),
    Atributo("disco_delantero_mm", "numero", "mm", 180, 340, parser=_mm),
    Atributo("abs", "enum", enum=("ninguno", "1 canal", "2 canales")),
    Atributo("cbs", "booleano"),
    Atributo("suspension_delantera", "texto"),
    Atributo("suspension_trasera", "texto"),
    Atributo("recorrido_delantero", "numero", "mm", 50, 320, parser=_mm),
    Atributo("llanta_delantera", "texto"),
    Atributo("llanta_trasera", "texto"),
    Atributo("consumo_declarado", "numero", "km/gal", 40, 400, parser=units.consumo_a_km_gal),
    Atributo("autonomia_declarada", "numero", "km", 20, 400, parser=_num),
    Atributo("iluminacion_led", "enum", enum=("no", "parcial", "completa")),
    Atributo("tablero", "enum", enum=("analogo", "mixto", "digital", "tft")),
    Atributo("conectividad", "booleano"),
]

ATRIBUTOS: dict[str, Atributo] = {a.clave: a for a in _A}
