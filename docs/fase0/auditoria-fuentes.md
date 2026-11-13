# Auditoría de fuentes — Fase 0

Fecha: 2026-11-13. Método: lectura de `robots.txt`, portada y página de términos de cada sitio
con un lector web automatizado. No es asesoría jurídica.

## Qué se pudo verificar y qué no

| Fuente | robots.txt | Términos de uso | Estado en `fuentes.yaml` |
|---|---|---|---|
| Honda (motos.honda.com.co, Fanalca) | Leído: `Allow: /` | **Leídos.** Prohíben reproducir los contenidos y limitan el uso de la información a la transacción "con la citación de la fuente" | `solo_manual` |
| Suzuki (suzuki.com.co) | Leído: Drupal estándar, solo bloquea admin y `/search/` | No se encontró página de términos | `pendiente_auditoria` |
| Yamaha (incolmotos-yamaha.com.co) | Leído: solo bloquea `/distribuidor/` | No se encontró página de términos | `pendiente_auditoria` |
| Hero (heromotos.com.co) | Leído: WordPress, solo `/wp-admin/` | Solo aviso de privacidad; sin términos | `pendiente_auditoria` |
| Vento (vento.com.co) | Leído: WordPress, solo `/wp-admin/` | Solo política de datos; sin términos | `pendiente_auditoria` |
| Auteco (auteco.com.co): TVS, Victory | Leído: **prohíbe toda URL con parámetros** (`Disallow: /*?`), búsqueda y vistas rápidas; permite `/api/catalog_system/` | No se encontró página de términos | `pendiente_auditoria` |
| Royal Enfield (royalenfield.com/co/es) | Leído: permite `/co*` | **Leídos.** Contenido "solely for personal, non-commercial use"; prohíbe reproducir y publicar | `pendiente_auditoria` |
| KTM fichas (ktm.com/es-co) | Leído (solo bloquea `/content/dam/` y similares) | **Leídos.** "No usage rights in and to the Content are granted"; prohíben publicar o duplicar el contenido con fines comerciales. Pesos y medidas "non-binding" | `pendiente_auditoria` |
| KTM precios (autocolombiana.com.co, importador) | Leído: `Allow: /`; bloquea `/*?`, filtros, `/Busca/`, `/checkout/` | Publicados solo los de datos personales; secciones 2 a 22 (incluida "De la oferta y el precio") son títulos sin texto | `pendiente_auditoria` |
| Bajaj (grupouma.com/colombia, Grupo UMA) | Leído: solo bloquea `/wp-admin/` y `*comparador*.webp` | **No verificado**: el enlace existe ("Términos y condiciones de uso web") pero no cargó | `pendiente_auditoria` |
| AKT (aktmotos.com, Grupo Corbeta) | **No verificado**: dominio confirmado, pero ninguna página cargó | **No verificado** | `pendiente_auditoria` |
| TVS / Victory (webs propias) | **No verificado** (tvsmotos.com.co, victorymotos.com.co no cargaron) | — | cubiertas vía Auteco |
| ANDI-Fenalco | andi.com.co: **no verificado**. fenalco.com.co: leído, no prohíbe nada | No se encontró la página del informe mensual | `solo_manual` (PDF) |

"No verificado" significa exactamente eso: el lector no pudo abrir el sitio (bloqueo del propio
lector o dominio equivocado). No significa que el sitio prohíba nada. Hay que abrirlos desde un
navegador normal.

## Hallazgos que cambian el plan

1. **Bajaj ya no es Auteco, y KTM tampoco (pero no va con Bajaj).** Grupo UMA es el distribuidor
   único de Bajaj desde el 3 de septiembre de 2020 ([El Carro Colombiano, 4-sep-2020](https://www.elcarrocolombiano.com/industria/bajaj-auto-nombra-al-grupo-uma-como-su-distribuidor-oficial-en-colombia/);
   vigente en mayo de 2026). Su web es `grupouma.com/colombia/`. KTM **no** pasó a Grupo UMA, como
   suponíamos: desde 2024 la comercializa **Autocolombiana** (grupo Autogermana) y Auteco solo la
   ensambla ([Portafolio, 24-oct-2023](https://www.portafolio.co/negocios/vehiculo/autocolombiana-vendera-motos-ktm-y-husqvarna-auteco-591117);
   Autocosmos la llama "importador oficial" en sept. de 2026).
2. **Honda tiene la cláusula más restrictiva.** Sus términos prohíben "Reproducir, copiar,
   representar, utilizar, distribuir, transformar o modificar los Contenidos" y restringen el uso
   de la información "sólo para fines de la transacción y con la citación de la fuente". Las
   especificaciones son hechos y en Colombia los hechos no tienen derechos de autor, pero aceptar
   el sitio es un contrato. Riesgo bajo mientras sea personal y gratuito; alto si se monetiza.
   Por eso Honda queda en carga manual con cita y enlace, y conviene pedir permiso a Fanalca.
3. **Royal Enfield** permite uso personal no comercial. Publicar una ficha en otra web ya es
   distribución; mismo análisis que Honda, menor severidad.
4. **Auteco obliga a un scraper concreto:** URLs limpias de producto o su API de catálogo VTEX
   (`/api/catalog_system/`), que el robots.txt permite explícitamente. Nada de filtros con `?`.
5. Ningún robots.txt leído bloquea las páginas de producto. Ninguna web leída menciona
   expresamente scraping o rastreo automatizado.

6. **KTM separa ficha y precio en dos dominios.** La ficha está en ktm.com (sin precios) y el precio
   en la tienda de Autocolombiana. Una versión de KTM necesita dos fuentes y un emparejamiento por
   nombre, y los años no coinciden: Autocolombiana vende la "200 DUKE 2027" y ktm.com publica la
   ficha 2026. Además, la 390 Duke tiene ficha pero no aparece a la venta en Autocolombiana.
7. **KTM declara dos pesos con etiquetas propias**: "Peso (sin combustible)" y "Peso con el depósito
   lleno". El primero no es peso seco (lleva aceite); va a `peso_sin_especificar`. El segundo se cargó
   como `peso_orden_marcha` con confianza media. La 250 y la 390 Duke dan ambas 165 kg, lo que huele a
   error de la página. KTM no publica rpm de potencia ni torque, ni canales de ABS ("ABS en curvas" no
   dice cuántos canales), así que el ABS quedó sin cargar.
8. **Bajaj publica precios en las tarjetas del menú** (leídas desde la página de preguntas frecuentes,
   2026-11-13, sin indicar si son sugeridos ni vigencia): Boxer CT100 KS $5.899.000, Boxer CT100 KS
   Boxer Racing $5.999.000, Boxer CT100 ES $6.199.000, Pulsar N160 Pro $10.999.000, Pulsar NS 160 FI ABS
   $11.199.000, Pulsar NS200 FI ABS SC $13.199.000, Dominar 400 Touring $19.399.000. No se cargaron en
   `precios.csv` porque no hay fichas de esas versiones todavía.

## Sobre los fallos del lector

El lector web automático no abrió aktmotos.com, grupouma.com/colombia/ (salvo preguntas frecuentes y
robots.txt), colombia.globalbajaj.com ni andi.com.co/robots.txt. Los errores fueron `client_error` o
"robots_disallowed" atribuido al propio proxy del lector, no a una regla del sitio: el robots.txt de
grupouma.com que sí se leyó no prohíbe nada. **Ninguno de esos fallos significa que el sitio prohíba el
acceso.** El contenedor y la VM del PC no tienen salida directa a internet.

## Reglas que el código ya aplica

- Ninguna fuente se descarga si no está en estado `aprobada` (hoy, ninguna lo está).
- El descargador lee robots.txt con comodines (RFC 9309; `urllib.robotparser` los ignora y daría
  por permitidas las URLs con `?` de Auteco), se identifica con un User-Agent con enlace al repo y
  espera 3 s o más entre peticiones.
- Solo se extraen hechos (ficha y precio). Nunca fotos ni textos de marketing; la web enlaza a la
  página oficial.

## Pendiente (requiere navegador humano o contacto)

- ~~Encontrar la web oficial de Bajaj, AKT y KTM~~ (hecho el 2026-11-13: grupouma.com/colombia,
  aktmotos.com, ktm.com/es-co + autocolombiana.com.co).
- Leer con un navegador normal: robots.txt y términos de aktmotos.com, "Términos y condiciones de
  uso web" de grupouma.com, y 4 fichas de AKT y 4 de Bajaj (Boxer CT100, Pulsar N160, NS200, Dominar 400).
- Leer completas las secciones 2 a 22 de los términos de Autocolombiana (puede que no estén publicadas).
- Confirmar que Suzuki, Yamaha y Auteco no tienen términos en otra ruta (pie de página con JS).
- Opcional pero recomendado: escribir a Fanalca (Honda) y a Auteco pidiendo permiso o un Excel.
