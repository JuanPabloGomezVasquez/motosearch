# motosearch

Comparador de motos para el mercado colombiano: fichas técnicas oficiales normalizadas,
comparación dentro del mismo segmento y gráficas con sentido estadístico.

**Estado: Fase 0.** Hay base de datos, pipeline de validación y una primera web estática con las
20 fichas manuales. No hay scrapers, a propósito.
La Fase 0 termina cuando existan 20 fichas manuales de 5 marcas validadas y la auditoría de
fuentes esté completa (`docs/fase0/auditoria-fuentes.md`).

## Estructura

```
db/
  migrations/0001_esquema_inicial.sql   Esquema PostgreSQL (versión como unidad, specs en formato largo)
  seed/0001_catalogos.sql               Segmentos, rangos ANDI, catálogo de atributos, 11 marcas MVP
  tests/smoke.sql                       Prueba de humo del esquema (CI)
pipeline/                               Python: normalización, validación, descarga cortés
  src/motosearch/config/fuentes.yaml    Registro de fuentes y su estado de auditoría
data/manual/                            Hojas de carga manual (fichas, descontinuadas, precios)
docs/fase0/                             Auditoría de fuentes
web/                                    Sitio estático (Astro): listado, ficha y comparador
  src/data/catalogo.json                Generado por `motosearch exportar`; no editar a mano
```

## Uso

```bash
cd pipeline
uv venv && uv pip install -e ".[dev]"
uv run pytest
uv run motosearch fuentes                                  # estado de cada fuente
uv run motosearch validar ../data/manual/fichas_fase0.csv  # valida la hoja manual
```

Web (lee solo `web/src/data/catalogo.json`):

```bash
cd pipeline && uv run motosearch exportar   # regenera el JSON tras editar las hojas
cd ../web && npm ci && npm run dev          # http://localhost:4321
```

Un test de `pipeline` falla si el JSON no está al día con las hojas.

Esquema en un Postgres local:

```bash
psql -f db/migrations/0001_esquema_inicial.sql -f db/seed/0001_catalogos.sql -f db/tests/smoke.sql
```

## Decisiones de diseño clave

- La unidad de comparación es la **versión** (modelo + generación + año + variante).
- Cada dato técnico guarda fuente, fecha, valor crudo, unidad original y confianza.
- Dato ausente = sin fila (NULL). Nunca 0.
- Peso seco y peso en orden de marcha son atributos distintos.
- Consumo declarado no es rankeable.
- Las versiones descontinuadas no llevan precio (lo impone un trigger).
- Ningún scraper corre contra una fuente no aprobada tras auditar robots.txt y términos.
