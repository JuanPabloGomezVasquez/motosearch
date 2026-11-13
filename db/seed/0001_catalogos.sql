-- Catálogos base. Los datos de motos NO van aquí: entran por el pipeline o carga manual.
BEGIN;

INSERT INTO segmento (slug, nombre, descripcion, criterio) VALUES
 ('trabajo',        'Trabajo / urbana básica', 'Uso diario y laboral, bajo costo', 'Posición erguida, rin 17-18, sin protección de viento, cc <= 125 y orientada a costo/consumo.'),
 ('scooter',        'Scooter', 'Transmisión automática CVT, plataforma para pies', 'CVT + plataforma plana. Si es CVT pero de rueda alta sin plataforma, sigue siendo scooter.'),
 ('naked',          'Naked / street', 'Calle, sin carenado completo', 'Sin carenado completo ni vocación off-road; incluye naked de 150 cc en adelante.'),
 ('doble-proposito','Doble propósito / enduro', 'Uso mixto calle y destapado', 'Llanta delantera >= 19 o 21 pulgadas, suspensión de recorrido largo y < 300 cc.'),
 ('sport',          'Sport / carenada', 'Carenado completo, posición deportiva', 'Carenado completo y manubrio bajo (clip-on o similar).'),
 ('adventure',      'Trail / adventure', 'Viaje y destapado, >= 250 cc', 'Vocación de viaje (parabrisas, tanque grande) y >= 250 cc. Doble propósito < 300 cc sin vocación de viaje va a doble-proposito.'),
 ('cruiser',        'Cruiser / clásica', 'Estética clásica o custom', 'Posición relajada o estética retro como argumento principal.'),
 ('semiautomatica', 'Semiautomática', 'Embrague automático, cambios con pie', 'Cambios secuenciales sin palanca de embrague.'),
 ('electrica',      'Eléctrica', 'Motor eléctrico', 'Motor eléctrico. Se compara por kW y autonomía, nunca por cc.');

-- Rangos de cilindraje como los publica ANDI-Fenalco (revisar contra cada boletín:
-- si el boletín cambia los cortes, se cambian aquí con una migración).
INSERT INTO rango_cilindraje (etiqueta, cc_min, cc_max) VALUES
 ('0-100 cc',    0,    100),
 ('101-125 cc',  100.1, 125),
 ('126-150 cc',  125.1, 150),
 ('151-200 cc',  150.1, 200),
 ('201-250 cc',  200.1, 250),
 ('251-400 cc',  250.1, 400),
 ('401-600 cc',  400.1, 600),
 ('601-1000 cc', 600.1, 1000),
 ('>1000 cc',    1000.1, NULL);

-- Catálogo cerrado de atributos. Rango min/max = validación de parser, no realidad del mercado.
INSERT INTO atributo (clave, nombre, grupo, tipo_valor, unidad, valores_enum, min_valido, max_valido, rankeable, nota_publica) VALUES
 ('cilindrada',          'Cilindrada',                'motor',       'numero', 'cc',     NULL, 49, 1900, TRUE, NULL),
 ('potencia_max',        'Potencia máxima',           'motor',       'numero', 'hp',     NULL, 2, 220, TRUE, 'Convertida a hp desde la unidad que declara la marca'),
 ('torque_max',          'Torque máximo',             'motor',       'numero', 'N·m',    NULL, 3, 250, TRUE, NULL),
 ('potencia_electrica',  'Potencia nominal (eléctrica)', 'motor',    'numero', 'kW',     NULL, 0.25, 100, TRUE, NULL),
 ('cilindros',           'Número de cilindros',       'motor',       'numero', NULL,     NULL, 1, 6, FALSE, NULL),
 ('tiempos',             'Tiempos',                   'motor',       'enum',   NULL,     ARRAY['2T','4T'], NULL, NULL, FALSE, NULL),
 ('refrigeracion',       'Refrigeración',             'motor',       'enum',   NULL,     ARRAY['aire','aceite','aire-aceite','liquida'], NULL, NULL, FALSE, NULL),
 ('alimentacion',        'Alimentación',              'motor',       'enum',   NULL,     ARRAY['carburador','inyeccion'], NULL, NULL, FALSE, NULL),
 ('norma_emisiones',     'Norma de emisiones',        'motor',       'enum',   NULL,     ARRAY['Euro 2','Euro 3','Euro 4','Euro 5','Euro 5+'], NULL, NULL, FALSE, NULL),
 ('arranque',            'Arranque',                  'motor',       'enum',   NULL,     ARRAY['electrico','pedal','electrico+pedal'], NULL, NULL, FALSE, NULL),
 ('transmision_tipo',    'Tipo de transmisión',       'transmision', 'enum',   NULL,     ARRAY['manual','semiautomatica','cvt','dct','directa'], NULL, NULL, FALSE, NULL),
 ('marchas',             'Número de marchas',         'transmision', 'numero', NULL,     NULL, 1, 7, FALSE, NULL),
 ('peso_seco',           'Peso en seco',              'dimensiones', 'numero', 'kg',     NULL, 60, 400, TRUE, 'Sin fluidos. No comparable con peso en orden de marcha'),
 ('peso_orden_marcha',   'Peso en orden de marcha',   'dimensiones', 'numero', 'kg',     NULL, 70, 450, TRUE, 'Con fluidos y tanque al 90% o lleno según marca'),
 ('capacidad_tanque',    'Capacidad del tanque',      'dimensiones', 'numero', 'L',      NULL, 3, 35, TRUE, NULL),
 ('altura_sillin',       'Altura del sillín',         'dimensiones', 'numero', 'mm',     NULL, 600, 1000, TRUE, NULL),
 ('distancia_ejes',      'Distancia entre ejes',      'dimensiones', 'numero', 'mm',     NULL, 1000, 1800, TRUE, NULL),
 ('distancia_piso',      'Distancia al piso',         'dimensiones', 'numero', 'mm',     NULL, 90, 350, TRUE, NULL),
 ('freno_delantero',     'Freno delantero',           'frenos',      'enum',   NULL,     ARRAY['tambor','disco','doble disco'], NULL, NULL, FALSE, NULL),
 ('freno_trasero',       'Freno trasero',             'frenos',      'enum',   NULL,     ARRAY['tambor','disco'], NULL, NULL, FALSE, NULL),
 ('disco_delantero_mm',  'Diámetro disco delantero',  'frenos',      'numero', 'mm',     NULL, 180, 340, TRUE, NULL),
 ('abs',                 'ABS',                       'frenos',      'enum',   NULL,     ARRAY['ninguno','1 canal','2 canales'], NULL, NULL, FALSE, NULL),
 ('cbs',                 'Frenado combinado (CBS)',   'frenos',      'booleano', NULL,   NULL, NULL, NULL, FALSE, NULL),
 ('suspension_delantera','Suspensión delantera',      'chasis',      'texto',  NULL,     NULL, NULL, NULL, FALSE, NULL),
 ('suspension_trasera',  'Suspensión trasera',        'chasis',      'texto',  NULL,     NULL, NULL, NULL, FALSE, NULL),
 ('recorrido_delantero', 'Recorrido susp. delantera', 'chasis',      'numero', 'mm',     NULL, 50, 320, TRUE, NULL),
 ('llanta_delantera',    'Llanta delantera',          'chasis',      'texto',  NULL,     NULL, NULL, NULL, FALSE, NULL),
 ('llanta_trasera',      'Llanta trasera',            'chasis',      'texto',  NULL,     NULL, NULL, NULL, FALSE, NULL),
 ('consumo_declarado',   'Consumo declarado',         'consumo',     'numero', 'km/gal', NULL, 40, 400, FALSE, 'Declarado por la marca, sin protocolo común. No se usa en rankings'),
 ('autonomia_declarada', 'Autonomía declarada (eléctrica)', 'consumo','numero', 'km',    NULL, 20, 400, FALSE, 'Declarada por la marca'),
 ('iluminacion_led',     'Iluminación LED',           'equipamiento','enum',   NULL,     ARRAY['no','parcial','completa'], NULL, NULL, FALSE, NULL),
 ('tablero',             'Tablero',                   'equipamiento','enum',   NULL,     ARRAY['analogo','mixto','digital','tft'], NULL, NULL, FALSE, NULL),
 ('conectividad',        'Conectividad con celular',  'equipamiento','booleano', NULL,   NULL, NULL, NULL, FALSE, NULL);

-- Empresas y marcas del MVP. "empresa" pendiente de verificar en Fase 0 (ver docs/fase0/auditoria-fuentes.md):
-- la web de Auteco en nov-2026 no mostraba Bajaj entre sus marcas.
INSERT INTO marca (slug, nombre, en_mvp, url_oficial) VALUES
 ('bajaj',         'Bajaj',         TRUE, NULL),
 ('suzuki',        'Suzuki',        TRUE, 'https://www.suzuki.com.co'),
 ('honda',         'Honda',         TRUE, 'https://motos.honda.com.co'),
 ('akt',           'AKT',           TRUE, NULL),
 ('yamaha',        'Yamaha',        TRUE, 'https://www.incolmotos-yamaha.com.co'),
 ('tvs',           'TVS',           TRUE, 'https://www.auteco.com.co'),
 ('hero',          'Hero',          TRUE, 'https://www.heromotos.com.co'),
 ('victory',       'Victory',       TRUE, 'https://www.auteco.com.co'),
 ('vento',         'Vento',         TRUE, 'https://www.vento.com.co'),
 ('ktm',           'KTM',           TRUE, NULL),
 ('royal-enfield', 'Royal Enfield', TRUE, 'https://www.royalenfield.com/co/es/');

COMMIT;
