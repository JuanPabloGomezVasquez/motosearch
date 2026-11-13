// Tipos y reglas de presentación compartidas por las páginas (servidor) y los scripts (cliente).
// La regla de oro: lo que no está en el JSON no existe. Nada de 0, promedios ni estimados.
import catalogo from "../data/catalogo.json";

export type Confianza = "alta" | "media" | "baja";

export interface Dato {
  valor: number | string | boolean;
  crudo: string;
  fuente_tipo: string;
  fuente_url: string;
  fecha: string;
  confianza: Confianza;
  notas: string | null;
  rpm?: number;
  unidad_original?: string;
}

export interface Precio {
  valor_cop: number;
  fecha: string;
  tipo: string;
  incluye_matricula: string | null;
  incluye_soat: string | null;
  fuente_url: string;
  notas: string | null;
}

export interface Version {
  slug: string;
  marca: string;
  marca_nombre: string;
  modelo: string;
  variante: string | null;
  anio_modelo: number;
  generacion: string;
  estado: "vigente" | "descontinuada";
  segmento: string;
  specs: Record<string, Dato>;
  precio: Precio | null;
}

export interface Atributo {
  nombre: string;
  grupo: string;
  tipo: "numero" | "texto" | "booleano" | "enum";
  unidad: string | null;
  rankeable: boolean;
  nota: string | null;
  orden: number;
}

export interface Catalogo {
  generado: string;
  atributos: Record<string, Atributo>;
  segmentos: Record<string, { nombre: string; descripcion: string; criterio: string }>;
  versiones: Version[];
}

export const CATALOGO = catalogo as unknown as Catalogo;

export const GRUPOS: Record<string, string> = {
  motor: "Motor",
  transmision: "Transmisión",
  dimensiones: "Dimensiones y peso",
  frenos: "Frenos",
  chasis: "Chasis y llantas",
  consumo: "Consumo",
  equipamiento: "Equipamiento",
};

const ENUM_LEGIBLE: Record<string, string> = {
  liquida: "Líquida",
  aire: "Aire",
  aceite: "Aceite",
  "aire-aceite": "Aire-aceite",
  inyeccion: "Inyección",
  carburador: "Carburador",
  electrico: "Eléctrico",
  pedal: "Pedal",
  "electrico+pedal": "Eléctrico y pedal",
  manual: "Manual",
  semiautomatica: "Semiautomática",
  cvt: "Automática (CVT)",
  dct: "Doble embrague (DCT)",
  directa: "Directa",
  tambor: "Tambor",
  disco: "Disco",
  "doble disco": "Doble disco",
  ninguno: "Sin ABS",
  "1 canal": "1 canal",
  "2 canales": "2 canales",
  no: "No",
  parcial: "Parcial",
  completa: "Completa",
  analogo: "Análogo",
  mixto: "Mixto",
  digital: "Digital",
  tft: "TFT",
};

// Datos que todo comprador espera ver. Si faltan, la ficha lo dice en voz alta.
export const CLAVES_ESENCIALES: { clave: string; nombre: string }[] = [
  { clave: "cilindrada", nombre: "Cilindrada" },
  { clave: "potencia_max", nombre: "Potencia" },
  { clave: "torque_max", nombre: "Torque" },
  { clave: "peso_tipado", nombre: "Peso con tipo declarado (seco u orden de marcha)" },
  { clave: "altura_sillin", nombre: "Altura del sillín" },
  { clave: "capacidad_tanque", nombre: "Capacidad del tanque" },
  { clave: "freno_delantero", nombre: "Freno delantero" },
  { clave: "abs", nombre: "ABS" },
];

export function faltantes(v: Version): string[] {
  return CLAVES_ESENCIALES.filter(({ clave }) => {
    if (clave === "peso_tipado") return !v.specs.peso_seco && !v.specs.peso_orden_marcha;
    return !v.specs[clave];
  }).map((c) => c.nombre);
}

const nf = (dec: number) =>
  new Intl.NumberFormat("es-CO", { maximumFractionDigits: dec, minimumFractionDigits: 0 });

export function formatoNumero(n: number, dec = 1): string {
  return nf(dec).format(n);
}

export function formatoCOP(n: number): string {
  return "$" + nf(0).format(n);
}

/** Texto tal como lo publica la marca, o null si el CSV guarda un valor ya clasificado (enum/booleano). */
export function textoPublicado(clave: string, d: Dato): string | null {
  const t = CATALOGO.atributos[clave]?.tipo;
  return t === "enum" || t === "booleano" ? null : d.crudo;
}

export function formatoValor(clave: string, d: Dato): string {
  const a = CATALOGO.atributos[clave];
  if (!a) return String(d.valor);
  if (a.tipo === "booleano") return d.valor ? "Sí" : "No";
  if (a.tipo === "enum") return ENUM_LEGIBLE[String(d.valor)] ?? String(d.valor);
  if (a.tipo === "texto") return String(d.valor);
  const dec = clave === "cilindrada" || a.unidad === "mm" ? 0 : 1;
  let s = formatoNumero(Number(d.valor), dec);
  if (a.unidad) s += a.unidad === "cc" ? " cc" : ` ${a.unidad}`;
  if (d.rpm) s += ` @ ${formatoNumero(d.rpm, 0)} rpm`;
  return s;
}

export function nombreVersion(v: Version): string {
  return [v.marca_nombre, v.modelo, v.variante].filter(Boolean).join(" ");
}

export const FUENTE_LEGIBLE: Record<string, string> = {
  web_marca: "Web oficial",
  pdf_marca: "Catálogo PDF oficial",
  manual_usuario: "Manual del propietario",
  concesionario: "Concesionario",
  revista: "Revista",
  archive_org: "Archivo web",
  otro: "Otra fuente",
};

export function url(ruta: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return base + ruta;
}

// ---------- Reglas de comparación ----------

export type TipoPeso = "peso_orden_marcha" | "peso_seco";

export const NOMBRE_TIPO_PESO: Record<TipoPeso, string> = {
  peso_orden_marcha: "en orden de marcha",
  peso_seco: "en seco",
};

/** Peso utilizable en comparaciones: solo con tipo declarado. Prefiere orden de marcha. */
export function pesoTipado(v: Version): { tipo: TipoPeso; dato: Dato } | null {
  if (v.specs.peso_orden_marcha) return { tipo: "peso_orden_marcha", dato: v.specs.peso_orden_marcha };
  if (v.specs.peso_seco) return { tipo: "peso_seco", dato: v.specs.peso_seco };
  return null;
}

export interface Barra {
  slug: string;
  valor: number | null; // null = sin dato o excluida
  etiqueta: string; // texto mostrado junto a la barra
  detalle: string; // tooltip: cómo lo publica la marca, fuente, confianza
  confianza?: Confianza;
  motivo?: string; // por qué no hay barra
}

export interface Grafica {
  id: string;
  titulo: string;
  unidad: string;
  barras: Barra[];
  nota?: string;
  publicable: boolean; // false si menos de 2 motos tienen dato comparable
}

const METRICAS_SIMPLES = [
  "cilindrada",
  "potencia_max",
  "torque_max",
  "capacidad_tanque",
  "altura_sillin",
  "distancia_ejes",
  "distancia_piso",
];

function detalle(clave: string, d: Dato): string {
  const f = FUENTE_LEGIBLE[d.fuente_tipo] ?? d.fuente_tipo;
  return `Publicado: “${d.crudo}” · ${f}, ${d.fecha} · confianza ${d.confianza}${d.notas ? " · " + d.notas : ""}`;
}

export function graficas(vs: Version[]): Grafica[] {
  const out: Grafica[] = [];
  for (const clave of METRICAS_SIMPLES) {
    const a = CATALOGO.atributos[clave];
    const barras: Barra[] = vs.map((v) => {
      const d = v.specs[clave];
      if (!d) return { slug: v.slug, valor: null, etiqueta: "sin dato", detalle: "", motivo: "La marca no lo publica" };
      return {
        slug: v.slug,
        valor: Number(d.valor),
        etiqueta: formatoValor(clave, d),
        detalle: detalle(clave, d),
        confianza: d.confianza,
      };
    });
    const conDato = barras.filter((b) => b.valor !== null).length;
    let nota: string | undefined;
    if (clave === "potencia_max" || clave === "torque_max") {
      const sinRpm = vs.filter((v) => v.specs[clave] && !v.specs[clave].rpm).length;
      if (sinRpm) nota = "Alguna marca no dice a qué rpm se logra; el valor pico se compara igual.";
    }
    if (clave === "potencia_max") {
      const unidades = new Set(vs.map((v) => v.specs[clave]?.unidad_original).filter(Boolean));
      if (unidades.size > 1)
        nota = (nota ? nota + " " : "") + "Convertida a hp desde la unidad que usa cada marca (hp, PS o CV).";
    }
    out.push({ id: clave, titulo: a.nombre, unidad: a.unidad ?? "", barras, nota, publicable: conDato >= 2 });
  }

  // Peso: solo entra el peso con tipo declarado, y solo se comparan motos con el MISMO tipo.
  const pesos = vs.map((v) => ({ v, p: pesoTipado(v) }));
  const conteo: Record<string, number> = {};
  for (const { p } of pesos) if (p) conteo[p.tipo] = (conteo[p.tipo] ?? 0) + 1;
  const tipo = (Object.entries(conteo).sort((a, b) => b[1] - a[1])[0]?.[0] ?? null) as TipoPeso | null;
  const barrasPeso: Barra[] = pesos.map(({ v, p }) => {
    if (!p) {
      const sin = v.specs.peso_sin_especificar;
      return {
        slug: v.slug,
        valor: null,
        etiqueta: "no comparable",
        detalle: "",
        motivo: sin
          ? `La marca publica ${formatoValor("peso_sin_especificar", sin)} sin decir si es seco o en orden de marcha`
          : "La marca no lo publica",
      };
    }
    if (p.tipo !== tipo) {
      return {
        slug: v.slug,
        valor: null,
        etiqueta: "no comparable",
        detalle: "",
        motivo: `Declara peso ${NOMBRE_TIPO_PESO[p.tipo]} (${formatoValor(p.tipo, p.dato)}); las demás, ${tipo ? NOMBRE_TIPO_PESO[tipo] : "otro tipo"}`,
      };
    }
    return {
      slug: v.slug,
      valor: Number(p.dato.valor),
      etiqueta: formatoValor(p.tipo, p.dato),
      detalle: detalle(p.tipo, p.dato),
      confianza: p.dato.confianza,
    };
  });
  const nPeso = barrasPeso.filter((b) => b.valor !== null).length;
  out.push({
    id: "peso",
    titulo: tipo ? `Peso ${NOMBRE_TIPO_PESO[tipo]}` : "Peso",
    unidad: "kg",
    barras: barrasPeso,
    nota: "Seco y en orden de marcha no se mezclan, y el peso sin tipo declarado no se grafica.",
    publicable: nPeso >= 2,
  });

  // Relación peso/potencia: mismas condiciones que el peso, más potencia publicada.
  const barrasRel: Barra[] = vs.map((v, i) => {
    const bp = barrasPeso[i];
    const pot = v.specs.potencia_max;
    if (bp.valor === null) return { slug: v.slug, valor: null, etiqueta: "no comparable", detalle: "", motivo: bp.motivo };
    if (!pot) return { slug: v.slug, valor: null, etiqueta: "sin dato", detalle: "", motivo: "La marca no publica la potencia" };
    const kgHp = bp.valor / Number(pot.valor);
    return {
      slug: v.slug,
      valor: Math.round(kgHp * 10) / 10,
      etiqueta: `${formatoNumero(kgHp, 1)} kg/hp`,
      detalle: `${bp.etiqueta} ÷ ${formatoValor("potencia_max", pot)}`,
      confianza: pot.confianza === "alta" && bp.confianza === "alta" ? "alta" : "media",
    };
  });
  out.push({
    id: "kg_hp",
    titulo: "Kilos por cada hp",
    unidad: "kg/hp",
    barras: barrasRel,
    nota: "Calculado aquí, no lo publica la marca. Menos kilos por hp es más aceleración, a igualdad de lo demás.",
    publicable: barrasRel.filter((b) => b.valor !== null).length >= 2,
  });

  // Precio sugerido: se grafica, pero cada marca define su "precio normal" a su manera.
  const barrasPrecio: Barra[] = vs.map((v) => {
    if (!v.precio)
      return {
        slug: v.slug,
        valor: null,
        etiqueta: "sin dato",
        detalle: "",
        motivo: v.estado === "descontinuada" ? "Descontinuada: no lleva precio" : "Precio no cargado (ver nota de la ficha)",
      };
    return {
      slug: v.slug,
      valor: v.precio.valor_cop,
      etiqueta: formatoCOP(v.precio.valor_cop),
      detalle: `Precio sugerido sin bonos, consultado el ${v.precio.fecha}${v.precio.notas ? " · " + v.precio.notas : ""}`,
    };
  });
  out.push({
    id: "precio",
    titulo: "Precio sugerido",
    unidad: "COP",
    barras: barrasPrecio,
    nota: "Precio de lista sin bonos ni financiación. No incluye matrícula ni SOAT (Honda no lo aclara).",
    publicable: barrasPrecio.filter((b) => b.valor !== null).length >= 2,
  });
  return out;
}
