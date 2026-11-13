-- Prueba de humo del esquema: se corre en CI sobre una base vacía con migración + seed.
\set ON_ERROR_STOP 1
BEGIN;
INSERT INTO fuente (tipo, nombre, url, es_oficial) VALUES ('web_marca', 'Prueba', 'https://example.com', TRUE);
INSERT INTO modelo (marca_id, slug, nombre_comercial) SELECT id, 'v-strom-650', 'V-Strom 650' FROM marca WHERE slug = 'suzuki';
INSERT INTO generacion (modelo_id, nombre, anio_inicio, anio_fin) SELECT id, '2012-2016', 2012, 2016 FROM modelo WHERE slug = 'v-strom-650';
INSERT INTO version (generacion_id, anio_modelo, variante, slug, estado, segmento_id, dato_historico)
  SELECT g.id, 2014, 'ABS', 'smoke-v-strom-2014', 'descontinuada', s.id, TRUE
  FROM generacion g, segmento s WHERE g.nombre = '2012-2016' AND s.slug = 'adventure';
INSERT INTO especificacion (version_id, atributo, valor_num, a_rpm, unidad_original, valor_crudo, fuente_id, confianza)
  SELECT v.id, 'potencia_max', 68.0, 8800, 'ps', 'prueba', f.id, 'media' FROM version v, fuente f WHERE v.slug = 'smoke-v-strom-2014';
DO $$
BEGIN
  IF (SELECT potencia_hp FROM ficha_actual WHERE slug = 'smoke-v-strom-2014') IS DISTINCT FROM 68.0 THEN
    RAISE EXCEPTION 'ficha_actual no refleja la especificación vigente';
  END IF;
  BEGIN
    INSERT INTO precio (version_id, fecha, valor_cop, tipo, fuente_id)
      SELECT v.id, CURRENT_DATE, 30000000, 'sugerido_marca', f.id FROM version v, fuente f WHERE v.slug = 'smoke-v-strom-2014';
    RAISE EXCEPTION 'se aceptó precio para una versión descontinuada';
  EXCEPTION WHEN raise_exception THEN
    IF SQLERRM LIKE 'se aceptó%' THEN RAISE; END IF;
  END;
END $$;
ROLLBACK;
\echo 'smoke OK'
