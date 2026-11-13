"""Validación de la hoja manual (formato largo) y de lo que produzcan los parsers.

Un error bloquea la carga; una advertencia la deja pasar pero exige revisión humana.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .atributos import ATRIBUTOS
from .units import potencia_a_hp, torque_a_nm

COLUMNAS_FICHAS = [
    "marca", "modelo", "generacion", "anio_modelo", "variante", "estado", "segmento",
    "atributo", "valor_crudo", "fuente_tipo", "fuente_url", "fecha_consulta", "confianza", "notas",
]
SEGMENTOS = {
    "trabajo", "scooter", "naked", "doble-proposito", "sport", "adventure",
    "cruiser", "semiautomatica", "electrica",
}
FUENTE_TIPOS = {
    "web_marca", "pdf_marca", "concesionario", "revista", "manual_usuario", "archive_org", "otro",
}
MARCAS_MVP = {
    "bajaj", "suzuki", "honda", "akt", "yamaha", "tvs", "hero", "victory", "vento", "ktm",
    "royal-enfield",
}
VERDADERO = {"si", "sí", "true", "1", "yes"}
FALSO = {"no", "false", "0"}


@dataclass
class ValorNormalizado:
    valor_num: float | None = None
    valor_texto: str | None = None
    valor_bool: bool | None = None
    a_rpm: int | None = None
    unidad_original: str | None = None


@dataclass
class Resultado:
    errores: list[str] = field(default_factory=list)
    advertencias: list[str] = field(default_factory=list)
    filas_ok: int = 0

    @property
    def ok(self) -> bool:
        return not self.errores


def normalizar(atributo: str, crudo: str) -> tuple[ValorNormalizado | None, str | None]:
    """Devuelve (valor, None) o (None, motivo_del_error)."""
    a = ATRIBUTOS.get(atributo)
    if a is None:
        return None, f"atributo desconocido '{atributo}' (añádelo al catálogo con una migración)"
    crudo = crudo.strip()
    if not crudo:
        return None, "valor vacío: si no hay dato, no pongas la fila (ausente = nulo)"
    if a.tipo == "texto":
        return ValorNormalizado(valor_texto=crudo), None
    if a.tipo == "booleano":
        c = crudo.lower()
        if c in VERDADERO:
            return ValorNormalizado(valor_bool=True), None
        if c in FALSO:
            return ValorNormalizado(valor_bool=False), None
        return None, f"booleano no reconocido '{crudo}'"
    if a.tipo == "enum":
        mapa = {e.lower(): e for e in a.enum}
        if crudo.lower() not in mapa:
            return None, f"'{crudo}' no es un valor permitido: {', '.join(a.enum)}"
        return ValorNormalizado(valor_texto=mapa[crudo.lower()]), None
    # numérico
    v = ValorNormalizado()
    if atributo == "potencia_max":
        r = potencia_a_hp(crudo)
        if r is None:
            return None, f"potencia sin unidad reconocible (hp, PS, CV, kW): '{crudo}'"
        v.valor_num, v.a_rpm, v.unidad_original = r[0], r[1].a_rpm, r[1].unidad_original
    elif atributo == "torque_max":
        r = torque_a_nm(crudo)
        if r is None:
            return None, f"torque sin unidad reconocible (N·m, kgf·m, lb·ft): '{crudo}'"
        v.valor_num, v.a_rpm, v.unidad_original = r[0], r[1].a_rpm, r[1].unidad_original
    else:
        v.valor_num = a.parser(crudo) if a.parser else None
        if v.valor_num is None:
            return None, f"no se pudo leer un número con unidad válida en '{crudo}'"
    if a.minimo is not None and v.valor_num < a.minimo:
        return None, f"{v.valor_num} {a.unidad or ''} está bajo el mínimo plausible ({a.minimo})"
    if a.maximo is not None and v.valor_num > a.maximo:
        return None, f"{v.valor_num} {a.unidad or ''} supera el máximo plausible ({a.maximo})"
    return v, None


def validar_fichas(ruta: Path) -> Resultado:
    res = Resultado()
    with ruta.open(encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        faltan = [c for c in COLUMNAS_FICHAS if c not in (lector.fieldnames or [])]
        if faltan:
            res.errores.append(f"faltan columnas: {', '.join(faltan)}")
            return res
        vistos: dict[tuple, str] = {}
        segmento_por_version: dict[tuple, str] = {}
        atributos_por_version: dict[tuple, set[str]] = {}
        for n, fila in enumerate(lector, start=2):
            pref = f"línea {n}"
            errores_fila: list[str] = []
            marca = fila["marca"].strip().lower()
            if marca not in MARCAS_MVP:
                res.advertencias.append(f"{pref}: marca '{marca}' fuera del MVP")
            try:
                anio = int(fila["anio_modelo"])
                if not 1950 <= anio <= date.today().year + 1:
                    errores_fila.append(f"año {anio} fuera de rango")
            except ValueError:
                errores_fila.append(f"año inválido '{fila['anio_modelo']}'")
                anio = None
            estado = fila["estado"].strip()
            if estado not in ("vigente", "descontinuada"):
                errores_fila.append(f"estado '{estado}' debe ser vigente o descontinuada")
            if not fila["generacion"].strip():
                errores_fila.append("falta generación (p. ej. '2020-2026')")
            seg = fila["segmento"].strip()
            if seg not in SEGMENTOS:
                errores_fila.append(f"segmento '{seg}' no existe")
            if fila["fuente_tipo"].strip() not in FUENTE_TIPOS:
                errores_fila.append(f"fuente_tipo '{fila['fuente_tipo']}' no válido")
            if not fila["fuente_url"].strip().startswith(("http://", "https://")):
                errores_fila.append("toda fila necesita fuente_url (trazabilidad)")
            try:
                date.fromisoformat(fila["fecha_consulta"].strip())
            except ValueError:
                errores_fila.append("fecha_consulta debe ser AAAA-MM-DD")
            if fila["confianza"].strip() not in ("alta", "media", "baja"):
                errores_fila.append("confianza debe ser alta, media o baja")
            if estado == "descontinuada" and fila["fuente_tipo"].strip() == "web_marca":
                res.advertencias.append(
                    f"{pref}: descontinuada con fuente web_marca; ¿es una página archivada?"
                )
            _, motivo = normalizar(fila["atributo"].strip(), fila["valor_crudo"])
            if motivo:
                errores_fila.append(f"{fila['atributo']}: {motivo}")

            clave_version = (marca, fila["modelo"].strip().lower(), anio, fila["variante"].strip().lower())
            clave = (*clave_version, fila["atributo"].strip())
            if clave in vistos:
                errores_fila.append(f"atributo repetido para la misma versión (ver {vistos[clave]})")
            vistos[clave] = pref
            previo = segmento_por_version.setdefault(clave_version, seg)
            if previo != seg:
                errores_fila.append(f"la versión tiene dos segmentos: '{previo}' y '{seg}'")
            atributos_por_version.setdefault(clave_version, set()).add(fila["atributo"].strip())

            if errores_fila:
                res.errores.extend(f"{pref}: {e}" for e in errores_fila)
            else:
                res.filas_ok += 1

        for v, attrs in atributos_por_version.items():
            if not attrs & {"peso_seco", "peso_orden_marcha", "peso_sin_especificar"}:
                res.advertencias.append(f"{v}: sin peso")
            if "cilindrada" not in attrs and "potencia_electrica" not in attrs:
                res.advertencias.append(f"{v}: sin cilindrada ni potencia eléctrica")
    return res


def verificar_cobertura(actual: int, anterior: int | None, umbral: float = 0.8) -> str | None:
    """Alerta del diseño: si una fuente trae < 80% de las versiones de la corrida anterior, se detiene."""
    if not anterior:
        return None
    if actual < anterior * umbral:
        return (
            f"cobertura cayó de {anterior} a {actual} versiones (< {umbral:.0%}). "
            "Lote detenido: probablemente cambió el diseño de la web."
        )
    return None
