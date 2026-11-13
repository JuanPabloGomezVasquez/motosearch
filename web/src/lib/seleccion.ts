// Selección del comparador (cliente). Se guarda en localStorage como comodidad; la fuente de
// verdad al comparar es la URL (?v=a,b,c), que se puede compartir.
export const MAX = 3;
const CLAVE = "motosearch:seleccion";

export function leer(): string[] {
  try {
    const v = JSON.parse(localStorage.getItem(CLAVE) ?? "[]");
    return Array.isArray(v) ? v.filter((s) => typeof s === "string").slice(0, MAX) : [];
  } catch {
    return [];
  }
}

export function guardar(slugs: string[]): void {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(slugs.slice(0, MAX)));
  } catch {
    /* modo privado o almacenamiento bloqueado: la selección dura solo esta página */
  }
  document.dispatchEvent(new CustomEvent("seleccion", { detail: slugs }));
}

export function alternar(slug: string): string[] {
  const s = leer();
  const i = s.indexOf(slug);
  if (i >= 0) s.splice(i, 1);
  else if (s.length < MAX) s.push(slug);
  guardar(s);
  return s;
}
