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
| KTM | `ktm.com/robots.txt` leído (solo bloquea `/content/dam/` y similares) | **No verificado**: la página de Colombia no cargó | `pendiente_auditoria` |
| Bajaj | **No verificado** | **No verificado** | `pendiente_auditoria` |
| AKT | **No verificado**: ningún dominio probado respondió | **No verificado** | `pendiente_auditoria` |
| TVS / Victory (webs propias) | **No verificado** (tvsmotos.com.co, victorymotos.com.co no cargaron) | — | cubiertas vía Auteco |
| ANDI-Fenalco | **No verificado** | — | `solo_manual` (PDF) |

"No verificado" significa exactamente eso: el lector no pudo abrir el sitio (bloqueo del propio
lector o dominio equivocado). No significa que el sitio prohíba nada. Hay que abrirlos desde un
navegador normal.

## Hallazgos que cambian el plan

1. **Bajaj ya no es Auteco.** El documento de diseño decía "Bajaj (Auteco)". Según prensa, Bajaj
   Auto nombró a Grupo UMA distribuidor oficial, y la portada de Auteco hoy muestra TVS, Victory,
   Kymco, Benelli, Kawasaki, Zontes y Ceronte, no Bajaj. La marca número 1 en ventas no tiene
   todavía una fuente identificada. Es probable que KTM (propiedad de Bajaj) siga el mismo camino;
   sin verificar.
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

## Reglas que el código ya aplica

- Ninguna fuente se descarga si no está en estado `aprobada` (hoy, ninguna lo está).
- El descargador lee robots.txt con comodines (RFC 9309; `urllib.robotparser` los ignora y daría
  por permitidas las URLs con `?` de Auteco), se identifica con un User-Agent con enlace al repo y
  espera 3 s o más entre peticiones.
- Solo se extraen hechos (ficha y precio). Nunca fotos ni textos de marketing; la web enlaza a la
  página oficial.

## Pendiente (requiere navegador humano o contacto)

- Encontrar la web oficial de Bajaj (Grupo UMA), AKT y KTM Colombia, y leer su robots.txt y términos.
- Confirmar que Suzuki, Yamaha y Auteco no tienen términos en otra ruta (pie de página con JS).
- Opcional pero recomendado: escribir a Fanalca (Honda) y a Auteco pidiendo permiso o un Excel.
