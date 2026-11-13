// Genera dist-relativo/: una copia del sitio que funciona sin servidor ni rutas absolutas
// (abrir desde disco o publicar en un visor que sirve archivos sueltos). Uso: npm run copia-relativa
import { cpSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { join, relative, sep } from "node:path";

const ORIGEN = "dist";
const DESTINO = "dist-relativo";
rmSync(DESTINO, { recursive: true, force: true });
cpSync(ORIGEN, DESTINO, { recursive: true });

const html = [];
(function recorrer(d) {
  for (const f of readdirSync(d)) {
    const p = join(d, f);
    if (statSync(p).isDirectory()) recorrer(p);
    else if (p.endsWith(".html")) html.push(p);
  }
})(DESTINO);

for (const archivo of html) {
  const profundidad = relative(DESTINO, archivo).split(sep).length - 1;
  const raiz = "../".repeat(profundidad);
  let t = readFileSync(archivo, "utf8");
  t = t.replace(/(href|src|data-base)="\/(?!\/)([^"]*)"/g, (_, attr, ruta) => {
    let r = ruta;
    if (!r.startsWith("assets/") && !/\.[a-z0-9]+$/i.test(r.split("?")[0])) {
      r = r.replace(/(^|\/)(\?|$)/, "$1index.html$2");
    }
    return `${attr}="${raiz}${r}"`;
  });
  t = t.replace("<head>", `<head><meta name="motosearch-raiz" content="${raiz}">`);
  writeFileSync(archivo, t);
}
console.log(`${html.length} páginas reescritas en ${DESTINO}/`);

// Página de entrada sin <html>/<head>/<body> propios, para visores que envuelven la página
// (p. ej. un Artifact de claude.ai): head + body + lo que Astro deja tras </html>.
{
  const t = readFileSync(join(DESTINO, "index.html"), "utf8");
  const head = t.match(/<head>([\s\S]*)<\/head>/)[1]
    .replace(/<meta charset="utf-8"\s*\/?>|<meta name="viewport"[^>]*>/g, "")
    .replace(/<title>[^<]*<\/title>/, "<title>motosearch</title>");
  const body = t.match(/<body[^>]*>([\s\S]*)<\/body>/)[1];
  const cola = t.split("</html>")[1] ?? "";
  writeFileSync("dist-relativo-entrada.html", head + body + cola);
  console.log("Entrada sin envoltura en dist-relativo-entrada.html");
}
