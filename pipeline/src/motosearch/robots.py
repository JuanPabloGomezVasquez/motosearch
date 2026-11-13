"""Intérprete de robots.txt según RFC 9309 (comodines * y $, la regla más larga gana).

No usamos urllib.robotparser porque ignora los comodines: con el robots.txt de
Auteco (``Disallow: /*?``) diría que cualquier URL con parámetros está permitida,
y no lo está.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass
class _Grupo:
    agentes: list[str] = field(default_factory=list)
    reglas: list[tuple[bool, str]] = field(default_factory=list)  # (permitir, patrón)


def _patron_a_regex(patron: str) -> re.Pattern[str]:
    ancla = patron.endswith("$")
    if ancla:
        patron = patron[:-1]
    cuerpo = ".*".join(re.escape(p) for p in patron.split("*"))
    return re.compile("^" + cuerpo + ("$" if ancla else ""))


class Robots:
    def __init__(self, texto: str):
        self.grupos: list[_Grupo] = []
        self.sitemaps: list[str] = []
        actual: _Grupo | None = None
        ultima_fue_agente = False
        for linea in texto.splitlines():
            linea = linea.split("#", 1)[0].strip()
            if not linea or ":" not in linea:
                continue
            clave, valor = (x.strip() for x in linea.split(":", 1))
            clave = clave.lower()
            if clave == "user-agent":
                if actual is None or not ultima_fue_agente:
                    actual = _Grupo()
                    self.grupos.append(actual)
                actual.agentes.append(valor.lower())
                ultima_fue_agente = True
                continue
            ultima_fue_agente = False
            if clave == "sitemap":
                self.sitemaps.append(valor)
            elif clave in ("allow", "disallow") and actual is not None:
                if valor == "" and clave == "disallow":
                    continue  # "Disallow:" vacío = permitir todo
                actual.reglas.append((clave == "allow", valor))

    def _reglas_para(self, agente: str) -> list[tuple[bool, str]]:
        agente = agente.lower()
        especificos = [g for g in self.grupos if any(a != "*" and a in agente for a in g.agentes)]
        grupos = especificos or [g for g in self.grupos if "*" in g.agentes]
        # Varios grupos con el mismo agente se combinan (RFC 9309, 2.2.1).
        return [r for g in grupos for r in g.reglas]

    def permitido(self, url: str, agente: str) -> bool:
        partes = urlsplit(url)
        ruta = (partes.path or "/") + (f"?{partes.query}" if partes.query else "")
        mejor: tuple[int, bool] | None = None
        for permitir, patron in self._reglas_para(agente):
            if not patron.startswith(("/", "*")):
                patron = "/" + patron
            if _patron_a_regex(patron).match(ruta):
                largo = len(patron)
                # Más largo gana; en empate gana Allow (la opción menos restrictiva).
                if mejor is None or largo > mejor[0] or (largo == mejor[0] and permitir):
                    mejor = (largo, permitir)
        return True if mejor is None else mejor[1]
