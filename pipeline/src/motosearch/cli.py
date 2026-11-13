"""CLI: ``motosearch validar <csv>``, ``motosearch fuentes`` y ``motosearch exportar``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .exportar import RAIZ, ErrorExportacion, escribir, exportar
from .fuentes import cargar_fuentes
from .validacion import validar_fichas


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="motosearch")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validar", help="valida una hoja de fichas en formato largo")
    v.add_argument("csv", type=Path)
    sub.add_parser("fuentes", help="lista fuentes y su estado de auditoría")
    e = sub.add_parser("exportar", help="exporta fichas y precios validados al JSON de la web")
    e.add_argument("--fichas", type=Path, default=RAIZ / "data" / "manual" / "fichas_fase0.csv")
    e.add_argument("--precios", type=Path, default=RAIZ / "data" / "manual" / "precios.csv")
    e.add_argument("--salida", type=Path, default=RAIZ / "web" / "src" / "data" / "catalogo.json")
    a = p.parse_args(argv)

    if a.cmd == "fuentes":
        for f in cargar_fuentes().values():
            print(f"{f.estado:20} {f.id:20} {', '.join(f.marcas) or '-'}")
        return 0

    if a.cmd == "exportar":
        try:
            datos = exportar(a.fichas, a.precios)
        except ErrorExportacion as err:
            print(f"ERROR  {err}")
            return 1
        escribir(datos, a.salida)
        print(f"{len(datos['versiones'])} versiones exportadas a {a.salida}")
        return 0

    r = validar_fichas(a.csv)
    for e in r.errores:
        print(f"ERROR  {e}")
    for w in r.advertencias:
        print(f"AVISO  {w}")
    print(f"\n{r.filas_ok} filas válidas, {len(r.errores)} errores, {len(r.advertencias)} avisos")
    return 0 if r.ok else 1


if __name__ == "__main__":
    sys.exit(main())
