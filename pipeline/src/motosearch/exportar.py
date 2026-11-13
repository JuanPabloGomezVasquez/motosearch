"""Exporta la hoja manual validada a un JSON estático para la web.

Es el puente de la Fase 0 mientras no hay Postgres en producción: la web lee solo este JSON.
Reglas que se mantienen al exportar:
* Solo sale lo que pasa la validación. Si la hoja tiene errores, no se exporta nada.
* Cada dato conserva valor crudo, fuente, fecha, confianza y notas.
* Dato ausente = clave ausente. Nunca 0.
* Los nombres, grupos y la marca "rankeable" de cada atributo salen del seed SQL, que es la
  fuente de verdad del catálogo.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

from .atributos import ATRIBUTOS
from .validacion import normalizar, validar_fichas

RAIZ = Path(__file__).resolve().parents[3]
SEED = RAIZ / "db" / "seed" / "0001_catalogos.sql"

NOMBRES_MARCA = {
    "bajaj": "Bajaj", "suzuki": "Suzuki", "honda": "Honda", "akt": "AKT", "yamaha": "Yamaha",
    "tvs": "TVS", "hero": "Hero", "victory": "Victory", "vento": "Vento", "ktm": "KTM",
    "royal-enfield": "Royal Enfield",
}


class ErrorExportacion(Exception):
    pass


def _tuplas_sql(bloque: str) -> list[list[str | None]]:
    """Lee las tuplas de un INSERT ... VALUES sencillo (cadenas, NULL, números, ARRAY[...])."""
    filas: list[list[str | None]] = []
    i, n = 0, len(bloque)
    while i < n:
        if bloque[i] == ";":
            break
        if bloque[i] != "(":
            i += 1
            continue
        i += 1
        campos: list[str | None] = []
        actual = ""
        en_cadena = False
        prof = 0
        es_cadena = False
        while i < n:
            c = bloque[i]
            if en_cadena:
                if c == "'" and i + 1 < n and bloque[i + 1] == "'":
                    actual += "'"
                    i += 2
                    continue
                if c == "'":
                    en_cadena = False
                else:
                    actual += c
            elif c == "'":
                en_cadena = True
                es_cadena = True
                actual = ""
            elif c == "[":
                prof += 1
                actual += c
            elif c == "]":
                prof -= 1
                actual += c
            elif c in ",)" and prof == 0:
                v = actual if es_cadena else actual.strip()
                campos.append(None if (not es_cadena and v.upper() == "NULL") else v)
                actual, es_cadena = "", False
                if c == ")":
                    i += 1
                    break
            else:
                actual += c
            i += 1
        filas.append(campos)
    return filas


def catalogo_desde_seed(ruta: Path = SEED) -> tuple[dict, dict]:
    sql = ruta.read_text(encoding="utf-8")
    bloque_attr = sql.split("INSERT INTO atributo", 1)[1].split("VALUES", 1)[1]
    atributos = {}
    for orden, f in enumerate(_tuplas_sql(bloque_attr)):
        clave, nombre, grupo, tipo, unidad, _enum, _mn, _mx, rankeable, nota = f
        atributos[clave] = {
            "nombre": nombre, "grupo": grupo, "tipo": tipo, "unidad": unidad,
            "rankeable": (rankeable or "").upper() == "TRUE", "nota": nota, "orden": orden,
        }
    bloque_seg = sql.split("INSERT INTO segmento", 1)[1].split("VALUES", 1)[1]
    segmentos = {
        f[0]: {"nombre": f[1], "descripcion": f[2], "criterio": f[3]}
        for f in _tuplas_sql(bloque_seg)
    }
    if set(atributos) != set(ATRIBUTOS):
        raise ErrorExportacion("el catálogo del seed SQL no coincide con atributos.py")
    return atributos, segmentos


def slugify(*partes: str) -> str:
    t = " ".join(p for p in partes if p)
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def _clave(marca: str, modelo: str, anio: str, variante: str) -> tuple:
    return (marca.strip().lower(), modelo.strip().lower(), anio.strip(), variante.strip().lower())


def exportar(fichas: Path, precios: Path | None = None) -> dict:
    res = validar_fichas(fichas)
    if not res.ok:
        raise ErrorExportacion("la hoja tiene errores; corre `motosearch validar` primero")
    atributos, segmentos = catalogo_desde_seed()

    versiones: dict[tuple, dict] = {}
    with fichas.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            k = _clave(fila["marca"], fila["modelo"], fila["anio_modelo"], fila["variante"])
            marca = k[0]
            v = versiones.setdefault(k, {
                "slug": slugify(marca, fila["modelo"], fila["variante"], fila["anio_modelo"]),
                "marca": marca,
                "marca_nombre": NOMBRES_MARCA.get(marca, marca.title()),
                "modelo": fila["modelo"].strip(),
                "variante": fila["variante"].strip() or None,
                "anio_modelo": int(fila["anio_modelo"]),
                "generacion": fila["generacion"].strip(),
                "estado": fila["estado"].strip(),
                "segmento": fila["segmento"].strip(),
                "specs": {},
                "precio": None,
            })
            attr = fila["atributo"].strip()
            val, _ = normalizar(attr, fila["valor_crudo"])
            dato = {
                "crudo": fila["valor_crudo"].strip(),
                "fuente_tipo": fila["fuente_tipo"].strip(),
                "fuente_url": fila["fuente_url"].strip(),
                "fecha": fila["fecha_consulta"].strip(),
                "confianza": fila["confianza"].strip(),
                "notas": fila["notas"].strip() or None,
            }
            if val.valor_num is not None:
                dato["valor"] = round(val.valor_num, 2)
            elif val.valor_bool is not None:
                dato["valor"] = val.valor_bool
            else:
                dato["valor"] = val.valor_texto
            if val.a_rpm:
                dato["rpm"] = val.a_rpm
            if val.unidad_original:
                dato["unidad_original"] = val.unidad_original
            v["specs"][attr] = dato

    if precios and precios.exists():
        with precios.open(encoding="utf-8", newline="") as f:
            for fila in csv.DictReader(f):
                k = _clave(fila["marca"], fila["modelo"], fila["anio_modelo"], fila["variante"])
                if k not in versiones:
                    raise ErrorExportacion(f"precio sin versión en fichas: {k}")
                if versiones[k]["estado"] != "vigente":
                    raise ErrorExportacion(f"una versión descontinuada no lleva precio: {k}")
                versiones[k]["precio"] = {
                    "valor_cop": int(fila["valor_cop"]),
                    "fecha": fila["fecha"].strip(),
                    "tipo": fila["tipo"].strip(),
                    "incluye_matricula": fila["incluye_matricula"].strip() or None,
                    "incluye_soat": fila["incluye_soat"].strip() or None,
                    "fuente_url": fila["fuente_url"].strip(),
                    "notas": fila["notas"].strip() or None,
                }

    slugs = [v["slug"] for v in versiones.values()]
    if len(slugs) != len(set(slugs)):
        raise ErrorExportacion("dos versiones generan el mismo slug")
    usados = {v["segmento"] for v in versiones.values()}
    return {
        "generado": max((d["fecha"] for v in versiones.values() for d in v["specs"].values()),
                        default=None),
        "atributos": atributos,
        "segmentos": {k: s for k, s in segmentos.items() if k in usados},
        "versiones": sorted(versiones.values(), key=lambda v: (v["segmento"], v["marca"], v["modelo"])),
    }


def escribir(datos: dict, salida: Path) -> None:
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
