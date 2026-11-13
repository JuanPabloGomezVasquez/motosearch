"""Descargador cortés: respeta robots.txt, se identifica, limita la tasa y guarda el crudo.

Ninguna fuente se descarga si su estado en ``config/fuentes.yaml`` no es ``aprobada``.
La aprobación es una decisión humana tras leer robots.txt y términos de uso.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx

from .fuentes import Fuente
from .robots import Robots

USER_AGENT = "motosearch-bot/0.1 (+https://github.com/JuanPabloGomezVasquez/motosearch)"
INTERVALO_MINIMO_S = 3.0


class FuenteNoAprobada(RuntimeError):
    pass


class BloqueadoPorRobots(RuntimeError):
    pass


@dataclass(frozen=True)
class Crudo:
    url: str
    status: int
    sha256: str
    ruta: Path
    capturado_en: datetime


class Fetcher:
    def __init__(self, fuente: Fuente, dir_crudo: Path, cliente: httpx.Client | None = None):
        if fuente.estado != "aprobada":
            raise FuenteNoAprobada(
                f"La fuente '{fuente.id}' está en estado '{fuente.estado}'. "
                "Apruébala en config/fuentes.yaml tras auditar robots.txt y términos."
            )
        self.fuente = fuente
        self.dir_crudo = dir_crudo
        self.cliente = cliente or httpx.Client(
            headers={"User-Agent": USER_AGENT}, timeout=30, follow_redirects=True
        )
        self.intervalo = max(INTERVALO_MINIMO_S, fuente.intervalo_s)
        self._robots: dict[str, Robots] = {}
        self._ultima: float = 0.0

    def _robots_de(self, url: str) -> Robots:
        p = urlsplit(url)
        host = f"{p.scheme}://{p.netloc}"
        if host not in self._robots:
            r = self.cliente.get(f"{host}/robots.txt")
            # 4xx = no hay restricciones (RFC 9309); 5xx = asumir todo prohibido.
            if r.status_code >= 500:
                self._robots[host] = Robots("User-agent: *\nDisallow: /")
            elif r.status_code >= 400:
                self._robots[host] = Robots("")
            else:
                self._robots[host] = Robots(r.text)
        return self._robots[host]

    def _esperar(self) -> None:
        faltante = self.intervalo - (time.monotonic() - self._ultima)
        if faltante > 0:
            time.sleep(faltante)
        self._ultima = time.monotonic()

    def descargar(self, url: str) -> Crudo:
        if not self._robots_de(url).permitido(url, USER_AGENT):
            raise BloqueadoPorRobots(url)
        self._esperar()
        r = self.cliente.get(url)
        contenido = r.content
        sha = hashlib.sha256(contenido).hexdigest()
        ahora = datetime.now(UTC)
        destino = self.dir_crudo / self.fuente.id / ahora.strftime("%Y-%m-%d") / f"{sha}.bin"
        destino.parent.mkdir(parents=True, exist_ok=True)
        if not destino.exists():
            destino.write_bytes(contenido)
        return Crudo(url=str(r.url), status=r.status_code, sha256=sha, ruta=destino, capturado_en=ahora)
