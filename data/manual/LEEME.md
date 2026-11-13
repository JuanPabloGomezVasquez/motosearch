# Carga manual (Fase 0)

Tres hojas en formato largo: **una fila por dato**, no una fila por moto. Es más incómodo de
llenar, pero cada dato lleva su fuente, fecha y confianza, que es lo que el diseño exige.

| Archivo | Qué va | Meta Fase 0 |
|---|---|---|
| `fichas_fase0.csv` | Versiones vigentes, desde la web oficial | 20 versiones de 5 marcas |
| `descontinuadas.csv` | Versiones descontinuadas por generación, sin precio | 5 de prueba (p. ej. V-Strom 650 ABS 2014) |
| `precios.csv` | Precio sugerido actual con fecha | Las mismas 20 vigentes |

Validar antes de hacer commit:

```bash
cd pipeline && uv run motosearch validar ../data/manual/fichas_fase0.csv
```

## Reglas

- **Si no hay dato, no hay fila.** Nunca `0`, `N/D` ni un valor estimado.
- `valor_crudo` se copia **tal cual** aparece en la fuente, con su unidad: `15,4 PS @ 8.500 rpm`,
  `1,4 kgf·m @ 7.000 rpm`, `142 kg`, `790 mm`. El validador convierte a la unidad canónica y
  rechaza lo que no entiende o lo que está fuera de rango.
- Peso: usa `peso_seco` o `peso_orden_marcha` según lo que diga la marca. Si la marca dice solo
  "peso", es `peso_seco` con confianza `baja` y una nota. No los mezcles.
- `segmento`: uno de `trabajo, scooter, naked, doble-proposito, sport, adventure, cruiser,
  semiautomatica, electrica`. Los criterios para casos límite están en `db/seed/0001_catalogos.sql`.
- `generacion`: rango de años, p. ej. `2012-2016`; si sigue vigente, `2021-`.
- Descontinuadas: `fuente_tipo` debe ser `manual_usuario`, `archive_org`, `revista` o `pdf_marca`.
  Pon en `notas` si la potencia se declaraba con otra norma.
- Atributos válidos: ver `pipeline/src/motosearch/atributos.py`.

## Lo que esta hoja tiene que responder

Si las 20 fichas no se pueden completar con confianza alta o media en los campos clave
(cilindrada, potencia, torque, peso, altura de sillín, tanque, frenos/ABS), el problema es la
fuente, no el código, y el plan de scrapers se replantea antes de escribirlo.
