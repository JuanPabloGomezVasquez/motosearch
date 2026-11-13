# Resultado de la hoja manual — Fase 0

Fecha: 2026-11-13. 20 versiones vigentes (año modelo 2027) de 5 marcas: Suzuki, Yamaha, Honda,
Hero y Vento, 4 por marca y una por segmento cuando fue posible. 380 datos, todos con URL de la
página oficial, fecha y confianza. `motosearch validar` pasa sin errores.

Los datos se copiaron de las páginas oficiales con un lector web automatizado, no con un
scraper. Honda se cargó así, con cita, por la restricción de sus términos.

## Qué tan completa queda cada ficha

| Dato clave | Versiones con dato | Comentario |
|---|---|---|
| Cilindrada | 20/20 | |
| Potencia | 19/20 | Falta la Gixxer FI 150 (Suzuki no la publica). Vento da 2 sin rpm |
| Torque | 18/20 | Faltan Gixxer FI 150 y Ovni 125 |
| Peso **con tipo declarado** | **6/20** | Tras revisar manuales: 4 Yamaha y la Gixxer en orden de marcha, la Address en seco (más la DIO en seco según un manual de 2017) |
| Altura de sillín | 12/20 | **Honda no la publica en ninguna de las 4** |
| Tanque | 18/20 | Honda solo en sus manuales (3 de 4), con confianza media |
| ABS con canales | 13/20 | Solo 3 lo dicen explícito; 10 inferidos de "Disco (ABS)" (confianza media) |

## Lo que esto significa para el diseño

1. **El peso es el problema principal, y los manuales no lo resolvieron.** Se revisaron manuales
   del propietario y catálogos PDF oficiales (Honda en su CDN, Suzuki y Hero en sus webs; Vento no
   publica manuales). Resultado:
   - Honda llama "peso neto" a algo que **no** es el peso en seco: la DIO tiene 104 kg "neto" en la
     web y 99 kg "en seco" en su manual.
   - Hero dice "peso sin carga" en web y manuales, sin definirlo.
   - En Suzuki, la web y el catálogo de la Gixxer se contradicen (el texto alternativo del ícono
     dice "en seco" en todas las motos; el catálogo dice "en orden de marcha").
   - Solo 6 de 20 versiones tienen un tipo de peso declarado.

   Decisión tomada: se crea el atributo `peso_sin_especificar`. Esos 14 pesos se muestran en la
   ficha con la etiqueta "tipo no declarado por la marca", pero **no entran** en la gráfica
   peso/potencia ni en comparaciones entre marcas. La gráfica peso/potencia queda limitada a las
   versiones con tipo declarado. Si eso la deja casi vacía, la única salida real es pedírselo a
   las marcas.
2. **Honda publica fichas cortas.** Ni la web ni los manuales traen altura de sillín, así que la
   gráfica de ergonomía queda sin Honda. El tanque salió de los manuales (2017 a 2019), que pueden
   ser de versiones anteriores a la 2027. La XR 190L no tiene manual publicado.
3. **Los precios no son comparables tal cual.** Cada marca publica tres o cuatro cifras (precio
   normal, con bono, con financiación, "desde"). Se cargó siempre el precio normal o "antes", sin
   bono, y la promoción va en `notas`. Ninguna marca incluye matrícula ni SOAT; Honda no lo dice.
4. **Errores en las propias webs oficiales**, que confirman que hace falta revisión humana:
   - Suzuki DR 150: "EURO 3" aparece bajo la etiqueta "Sistema de válvulas".
   - Honda XR 190L: la tabla dice 184 cc y el texto 184,43 cc.
   - Hero Xoom 125: "Precio desde $7.990.000" es mayor que "Precio antes $6.990.000". No se cargó
     su precio.
   - Hero Xpulse 200: la meta descripción y la página muestran precios distintos.
   - Hero Eco Deluxe: la web dice tanque de 10,5 L y el manual 9,5 L.
5. **Datos sospechosos**: la Vento Rapid 125 declara 10 hp con 6,9 N·m y 120 cc, más potencia que
   la Ovni 125 (8,1 hp) y que motos de 125 cc de marcas grandes. Queda con confianza media.

## Veredicto Fase 0

Las 20 fichas se pueden completar en lo básico (cilindrada, potencia, frenos, llantas) con
confianza alta. **No** se pueden completar con confianza en peso y ergonomía para Honda, Suzuki,
Hero y Vento. Antes de escribir scrapers hay que decidir de dónde sale el peso; un scraper solo
automatizaría la ambigüedad.

## Pendiente

- Descontinuadas (`descontinuadas.csv`): vacía; requiere manuales o archive.org.
- Generación de cada modelo (`generacion = "sin verificar"`): las webs no dicen desde qué año se vende.
- Suzuki: los 4 precios de noviembre tienen vigencia hasta el 30-nov-2026.

## Ampliación 2026-11-13: KTM (4 versiones)

Se añadieron 200 Duke 2026, 250 Duke 2027, 390 Duke 2027 y 390 Adventure X 2027, con 66 datos de
las fichas técnicas de ktm.com/es-co, y 3 precios de Autocolombiana (la 390 Duke no aparece a la
venta). Bajaj y AKT quedan sin fichas: sus webs no se pudieron leer con el lector automático
(detalle en `auditoria-fuentes.md`).

| Dato clave | KTM 4/4 | Comentario |
|---|---|---|
| Cilindrada, potencia, torque | 4/4 | Sin rpm en ninguna |
| Peso con tipo | 3/4, confianza media | "Peso con el depósito lleno" se asimiló a orden de marcha; la 200 Duke solo da "sin combustible" |
| Altura de sillín | 4/4 | La 390 Duke da "820/800 mm"; se tomó 800 |
| Tanque | 2/4 | Las fichas de 250 y 390 Duke no lo traen |
| ABS con canales | 0/4 | Dicen "ABS en curvas" sin canales; no se cargó |
