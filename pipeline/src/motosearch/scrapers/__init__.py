"""Scrapers por fuente. Ninguno implementado todavía, a propósito.

Fase 0 primero: la hoja manual de 20 fichas (data/manual/) dice qué campos publica cada
marca y en qué formato. Un scraper se escribe solo para una fuente en estado "aprobada" en
config/fuentes.yaml, y debe:

1. Descargar con ``motosearch.fetcher.Fetcher`` (robots.txt, User-Agent, 1 petición / 3+ s, crudo con hash).
2. Separar captura y parseo: ``parsear(crudo: bytes) -> list[FilaFicha]`` es una función pura,
   testeada contra crudos guardados en tests/fixtures/<fuente>/.
3. Pasar por ``validacion.normalizar`` y ``verificar_cobertura`` antes de proponer cambios.
4. Proponer los cambios como diff para revisión humana; nunca escribir directo a producción.
"""
