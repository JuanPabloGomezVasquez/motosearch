# Resultado de la hoja manual — Fase 0

Fecha: 2026-11-13. 20 versiones vigentes (año modelo 2027) de 5 marcas: Suzuki, Yamaha, Honda,
Hero y Vento, 4 por marca y una por segmento cuando fue posible. 375 datos, todos con URL de la
página oficial, fecha y confianza. `motosearch validar` pasa sin errores.

Los datos se copiaron de las páginas oficiales con un lector web automatizado, no con un
scraper. Honda se cargó así, con cita, por la restricción de sus términos.

## Qué tan completa queda cada ficha

| Dato clave | Versiones con dato | Comentario |
|---|---|---|
| Cilindrada | 20/20 | |
| Potencia | 19/20 | Falta la Gixxer FI 150 (Suzuki no la publica). Vento da 2 sin rpm |
| Torque | 18/20 | Faltan Gixxer FI 150 y Ovni 125 |
| Peso **con tipo claro** | **4/20** | Solo Yamaha dice "con aceite y tanque lleno". El resto dice "Peso", "Neto" o "sin carga" |
| Altura de sillín | 12/20 | **Honda no la publica en ninguna de las 4** |
| Tanque | 15/20 | **Honda no lo publica en ninguna de las 4** |
| ABS con canales | 13/20 | Solo 3 lo dicen explícito; 10 inferidos de "Disco (ABS)" (confianza media) |

## Lo que esto significa para el diseño

1. **El peso es el problema principal.** 16 de 20 fichas tienen un peso de tipo ambiguo, cargado
   como `peso_seco` con confianza baja o media. La gráfica peso/potencia del diseño **no se puede
   publicar** con estos datos sin mezclar peso seco con peso en orden de marcha, que es justo lo
   que el diseño prohíbe. Opciones: mostrarla solo para Yamaha, buscar el manual de usuario (suele
   traer el peso en orden de marcha) o preguntar a las marcas.
2. **Honda publica fichas cortas.** Sin altura de sillín ni tanque, la gráfica de ergonomía queda
   sin Honda. El manual de usuario o el catálogo PDF son la fuente lógica.
3. **Los precios no son comparables tal cual.** Cada marca publica tres o cuatro cifras (precio
   normal, con bono, con financiación, "desde"). Se cargó siempre el precio normal o "antes", sin
   bono, y la promoción va en `notas`. Ninguna marca incluye matrícula ni SOAT; Honda no lo dice.
4. **Errores en las propias webs oficiales**, que confirman que hace falta revisión humana:
   - Suzuki DR 150: "EURO 3" aparece bajo la etiqueta "Sistema de válvulas".
   - Honda XR 190L: la tabla dice 184 cc y el texto 184,43 cc.
   - Hero Xoom 125: "Precio desde $7.990.000" es mayor que "Precio antes $6.990.000". No se cargó
     su precio.
   - Hero Xpulse 200: la meta descripción y la página muestran precios distintos.
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
