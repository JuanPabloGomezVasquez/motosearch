"""Registro de fuentes y su estado de auditoría (config/fuentes.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

RUTA_FUENTES = Path(__file__).parent / "config" / "fuentes.yaml"

Estado = Literal["pendiente_auditoria", "aprobada", "solo_manual", "excluida"]


class Fuente(BaseModel):
    id: str
    nombre: str
    marcas: list[str]
    url: str | None = None
    estado: Estado
    metodo: Literal["html", "js", "pdf", "manual"] = "manual"
    intervalo_s: float = 5.0
    notas: str = ""


def cargar_fuentes(ruta: Path = RUTA_FUENTES) -> dict[str, Fuente]:
    datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    fuentes = [Fuente(**f) for f in datos["fuentes"]]
    return {f.id: f for f in fuentes}
