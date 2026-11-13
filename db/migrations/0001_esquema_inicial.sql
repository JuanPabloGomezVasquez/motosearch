-- motosearch: esquema inicial (PostgreSQL 15+)
-- Principios:
--   * La unidad de comparación es la VERSION (modelo + generación + año + variante).
--   * Cada dato técnico vive en formato largo (especificacion) con fuente, fecha,
--     valor crudo y confianza. La web lee una vista ancha derivada.
--   * Un dato ausente es NULL (no se inserta fila), nunca 0.
--   * El precio es un dato secundario, fechado y tipado; nunca se mezclan tipos.

BEGIN;

CREATE EXTENSION IF NOT EXISTS citext;

-- ---------------------------------------------------------------------------
-- Catálogo
-- ---------------------------------------------------------------------------

CREATE TABLE empresa (
    id          SERIAL PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,          -- Auteco, Fanalco, Incolmotos...
    rol         TEXT NOT NULL CHECK (rol IN ('ensamblador', 'importador', 'fabricante')),
    url         TEXT
);

CREATE TABLE marca (
    id          SERIAL PRIMARY KEY,
    slug        CITEXT NOT NULL UNIQUE,        -- 'bajaj', 'royal-enfield'
    nombre      TEXT NOT NULL,
    empresa_id  INT REFERENCES empresa(id),    -- quién la ensambla/importa en Colombia
    en_mvp      BOOLEAN NOT NULL DEFAULT FALSE,
    url_oficial TEXT
);

CREATE TABLE modelo (
    id          SERIAL PRIMARY KEY,
    marca_id    INT NOT NULL REFERENCES marca(id),
    slug        CITEXT NOT NULL,
    nombre_comercial TEXT NOT NULL,            -- 'NMAX 155'
    UNIQUE (marca_id, slug)
);

-- Nombre con el que el modelo aparece en RUNT / ANDI-Fenalco (p. ej. GPD155-A = NMAX 155).
CREATE TABLE modelo_alias (
    modelo_id   INT NOT NULL REFERENCES modelo(id) ON DELETE CASCADE,
    alias       CITEXT NOT NULL,
    origen      TEXT NOT NULL CHECK (origen IN ('runt', 'andi_fenalco', 'marca', 'otro')),
    PRIMARY KEY (modelo_id, alias)
);

-- Generación: rango de años en que se vendió en Colombia con la misma base técnica.
-- Permite comparar descontinuadas sin confundir una V-Strom 650 2005 con una 2014.
CREATE TABLE generacion (
    id          SERIAL PRIMARY KEY,
    modelo_id   INT NOT NULL REFERENCES modelo(id),
    nombre      TEXT NOT NULL,                 -- 'L2 (2012-2016)'
    anio_inicio SMALLINT NOT NULL CHECK (anio_inicio BETWEEN 1950 AND 2100),
    anio_fin    SMALLINT CHECK (anio_fin IS NULL OR anio_fin >= anio_inicio),  -- NULL = vigente
    cambios     TEXT,                          -- qué cambió frente a la anterior
    UNIQUE (modelo_id, nombre)
);

-- ---------------------------------------------------------------------------
-- Segmentación: dos ejes independientes (estilo y rango de cilindraje)
-- ---------------------------------------------------------------------------

CREATE TABLE segmento (
    id          SERIAL PRIMARY KEY,
    slug        CITEXT NOT NULL UNIQUE,        -- 'naked', 'scooter'...
    nombre      TEXT NOT NULL,
    descripcion TEXT,
    criterio    TEXT NOT NULL                  -- regla escrita para resolver casos límite
);

-- Rangos alineados con los del boletín ANDI-Fenalco para poder cruzar con ventas.
CREATE TABLE rango_cilindraje (
    id          SERIAL PRIMARY KEY,
    etiqueta    TEXT NOT NULL UNIQUE,          -- '101-125 cc'
    cc_min      NUMERIC(6,1) NOT NULL,
    cc_max      NUMERIC(6,1),                  -- NULL = sin tope
    CHECK (cc_max IS NULL OR cc_max >= cc_min)
);

CREATE TABLE version (
    id              SERIAL PRIMARY KEY,
    generacion_id   INT NOT NULL REFERENCES generacion(id),
    anio_modelo     SMALLINT NOT NULL CHECK (anio_modelo BETWEEN 1950 AND 2100),
    variante        TEXT NOT NULL DEFAULT '',  -- 'ABS', 'Rally', '' si es única
    slug            CITEXT NOT NULL UNIQUE,    -- 'suzuki-dr150-abs-2026'
    estado          TEXT NOT NULL CHECK (estado IN ('vigente', 'descontinuada')),
    es_electrica    BOOLEAN NOT NULL DEFAULT FALSE,
    segmento_id     INT REFERENCES segmento(id),       -- asignado a mano, no por algoritmo
    segmento_revisado BOOLEAN NOT NULL DEFAULT FALSE,
    dato_historico  BOOLEAN NOT NULL DEFAULT FALSE,    -- ficha reconstruida (manuales, archive.org, revistas)
    nota_historica  TEXT,                              -- p. ej. 'potencia declarada bajo norma anterior'
    url_oficial     TEXT,
    creado_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (generacion_id, anio_modelo, variante),
    CHECK (NOT dato_historico OR estado = 'descontinuada')
);

-- ---------------------------------------------------------------------------
-- Procedencia
-- ---------------------------------------------------------------------------

-- Una fuente es un origen estable (la web de la marca, un PDF, una revista).
CREATE TABLE fuente (
    id          SERIAL PRIMARY KEY,
    tipo        TEXT NOT NULL CHECK (tipo IN ('web_marca', 'pdf_marca', 'concesionario',
                                              'revista', 'manual_usuario', 'archive_org',
                                              'andi_fenalco', 'otro')),
    nombre      TEXT NOT NULL,
    url         TEXT,
    es_oficial  BOOLEAN NOT NULL DEFAULT FALSE
);

-- Una captura es una descarga concreta de una fuente, con su crudo guardado.
-- Si el parser falla, se re-procesa el crudo sin volver a pedir la página.
CREATE TABLE captura (
    id              BIGSERIAL PRIMARY KEY,
    fuente_id       INT NOT NULL REFERENCES fuente(id),
    url             TEXT NOT NULL,
    capturado_en    TIMESTAMPTZ NOT NULL,
    metodo          TEXT NOT NULL CHECK (metodo IN ('scraper', 'manual', 'pdf', 'api')),
    sha256          CHAR(64),                  -- hash del crudo
    ruta_crudo      TEXT,                      -- clave en el bucket (R2/S3) o ruta local
    http_status     SMALLINT,
    UNIQUE (url, sha256)
);

-- ---------------------------------------------------------------------------
-- Ficha técnica (formato largo)
-- ---------------------------------------------------------------------------

-- Catálogo cerrado de atributos con su unidad canónica. Añadir un atributo es una
-- decisión explícita (migración), no algo que un parser invente.
CREATE TABLE atributo (
    clave           TEXT PRIMARY KEY,          -- 'potencia_max'
    nombre          TEXT NOT NULL,
    grupo           TEXT NOT NULL,             -- 'motor', 'chasis', 'dimensiones'...
    tipo_valor      TEXT NOT NULL CHECK (tipo_valor IN ('numero', 'texto', 'booleano', 'enum')),
    unidad          TEXT,                      -- unidad canónica: 'hp', 'kg', 'mm'...
    valores_enum    TEXT[],                    -- para tipo enum
    min_valido      NUMERIC,                   -- validación de rango (detecta errores de parser)
    max_valido      NUMERIC,
    rankeable       BOOLEAN NOT NULL DEFAULT TRUE,  -- consumo declarado = FALSE
    nota_publica    TEXT                       -- etiqueta que la web muestra junto al dato
);

CREATE TABLE especificacion (
    id              BIGSERIAL PRIMARY KEY,
    version_id      INT NOT NULL REFERENCES version(id) ON DELETE CASCADE,
    atributo        TEXT NOT NULL REFERENCES atributo(clave),
    valor_num       NUMERIC,
    valor_texto     TEXT,
    valor_bool      BOOLEAN,
    a_rpm           INT CHECK (a_rpm IS NULL OR a_rpm BETWEEN 500 AND 20000),  -- potencia/torque
    unidad_original TEXT,                      -- 'PS', 'CV', 'kW', 'hp'...
    valor_crudo     TEXT NOT NULL,             -- tal cual aparece en la fuente
    captura_id      BIGINT REFERENCES captura(id),
    fuente_id       INT NOT NULL REFERENCES fuente(id),
    vigente_desde   TIMESTAMPTZ NOT NULL DEFAULT now(),
    vigente_hasta   TIMESTAMPTZ,               -- NULL = valor actual; historial por cierre
    confianza       TEXT NOT NULL CHECK (confianza IN ('alta', 'media', 'baja')),
    revisado_por    TEXT,                      -- NULL = pendiente de revisión humana
    CHECK (num_nonnulls(valor_num, valor_texto, valor_bool) = 1)
);

-- Solo un valor vigente por (version, atributo).
CREATE UNIQUE INDEX especificacion_vigente_uk
    ON especificacion (version_id, atributo) WHERE vigente_hasta IS NULL;

-- ---------------------------------------------------------------------------
-- Precio (secundario, fechado, tipado)
-- ---------------------------------------------------------------------------

CREATE TABLE precio (
    id                  BIGSERIAL PRIMARY KEY,
    version_id          INT NOT NULL REFERENCES version(id) ON DELETE CASCADE,
    fecha               DATE NOT NULL,
    valor_cop           BIGINT NOT NULL CHECK (valor_cop BETWEEN 1000000 AND 500000000),
    tipo                TEXT NOT NULL CHECK (tipo IN ('sugerido_marca', 'concesionario')),
    incluye_matricula   BOOLEAN,               -- NULL = la fuente no lo dice
    incluye_soat        BOOLEAN,
    captura_id          BIGINT REFERENCES captura(id),
    fuente_id           INT NOT NULL REFERENCES fuente(id),
    UNIQUE (version_id, fecha, tipo, fuente_id)
);

-- Regla del MVP: una versión descontinuada no lleva precio.
CREATE FUNCTION precio_solo_vigentes() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF (SELECT estado FROM version WHERE id = NEW.version_id) <> 'vigente' THEN
        RAISE EXCEPTION 'version % está descontinuada: no se registra precio', NEW.version_id;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER precio_solo_vigentes_trg
    BEFORE INSERT OR UPDATE ON precio
    FOR EACH ROW EXECUTE FUNCTION precio_solo_vigentes();

-- ---------------------------------------------------------------------------
-- Mercado (solo lo que publica ANDI-Fenalco; nada inferido)
-- ---------------------------------------------------------------------------

CREATE TABLE venta_mensual (
    id          SERIAL PRIMARY KEY,
    mes         DATE NOT NULL CHECK (EXTRACT(DAY FROM mes) = 1),
    nivel       TEXT NOT NULL CHECK (nivel IN ('total', 'marca', 'modelo', 'rango_cilindraje')),
    marca_id    INT REFERENCES marca(id),
    nombre_reportado TEXT,                     -- texto literal del boletín (marca o modelo)
    modelo_id   INT REFERENCES modelo(id),     -- solo si se pudo mapear con seguridad
    rango_id    INT REFERENCES rango_cilindraje(id),
    unidades    INT NOT NULL CHECK (unidades >= 0),
    fuente_id   INT NOT NULL REFERENCES fuente(id),
    CHECK (
        (nivel = 'total' AND marca_id IS NULL AND modelo_id IS NULL AND rango_id IS NULL) OR
        (nivel = 'marca' AND marca_id IS NOT NULL) OR
        (nivel = 'modelo' AND nombre_reportado IS NOT NULL) OR
        (nivel = 'rango_cilindraje' AND rango_id IS NOT NULL)
    )
);

-- ---------------------------------------------------------------------------
-- Calidad
-- ---------------------------------------------------------------------------

CREATE TABLE reporte_error (
    id          BIGSERIAL PRIMARY KEY,
    version_id  INT NOT NULL REFERENCES version(id) ON DELETE CASCADE,
    atributo    TEXT REFERENCES atributo(clave),
    mensaje     TEXT NOT NULL CHECK (length(mensaje) BETWEEN 5 AND 2000),
    creado_en   TIMESTAMPTZ NOT NULL DEFAULT now(),
    estado      TEXT NOT NULL DEFAULT 'abierto' CHECK (estado IN ('abierto', 'aceptado', 'rechazado'))
    -- Sin email ni nombre a propósito: no recoger datos personales (Ley 1581 de 2012).
);

-- Registro de cada corrida del pipeline: base de la alerta de caída de cobertura.
CREATE TABLE corrida (
    id              BIGSERIAL PRIMARY KEY,
    fuente_id       INT NOT NULL REFERENCES fuente(id),
    iniciada_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    terminada_en    TIMESTAMPTZ,
    versiones_encontradas INT,
    estado          TEXT NOT NULL CHECK (estado IN ('ok', 'detenida_cobertura', 'error')),
    detalle         TEXT
);

-- ---------------------------------------------------------------------------
-- Vista para la web: ficha ancha con solo valores vigentes
-- ---------------------------------------------------------------------------

CREATE VIEW ficha_actual AS
SELECT
    v.id            AS version_id,
    v.slug,
    ma.nombre       AS marca,
    mo.nombre_comercial AS modelo,
    g.nombre        AS generacion,
    v.anio_modelo,
    v.variante,
    v.estado,
    v.dato_historico,
    s.slug          AS segmento,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'cilindrada')            AS cilindrada_cc,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'potencia_max')          AS potencia_hp,
    MAX(e.a_rpm)      FILTER (WHERE e.atributo = 'potencia_max')          AS potencia_rpm,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'torque_max')            AS torque_nm,
    MAX(e.a_rpm)      FILTER (WHERE e.atributo = 'torque_max')            AS torque_rpm,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'peso_orden_marcha')     AS peso_orden_marcha_kg,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'peso_seco')             AS peso_seco_kg,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'peso_sin_especificar')  AS peso_sin_especificar_kg,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'altura_sillin')         AS altura_sillin_mm,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'capacidad_tanque')      AS tanque_l,
    MAX(e.valor_texto) FILTER (WHERE e.atributo = 'abs')                  AS abs,
    MAX(e.valor_num)  FILTER (WHERE e.atributo = 'consumo_declarado')     AS consumo_declarado_kmgal
FROM version v
JOIN generacion g ON g.id = v.generacion_id
JOIN modelo mo    ON mo.id = g.modelo_id
JOIN marca ma     ON ma.id = mo.marca_id
LEFT JOIN segmento s ON s.id = v.segmento_id
LEFT JOIN especificacion e ON e.version_id = v.id AND e.vigente_hasta IS NULL
GROUP BY v.id, ma.nombre, mo.nombre_comercial, g.nombre, s.slug;

-- Precio vigente: el último sugerido por la marca, con su fecha.
CREATE VIEW precio_actual AS
SELECT DISTINCT ON (version_id)
    version_id, fecha, valor_cop, incluye_matricula, incluye_soat, fuente_id
FROM precio
WHERE tipo = 'sugerido_marca'
ORDER BY version_id, fecha DESC;

COMMIT;
