import csv
import re
from pathlib import Path

from motosearch.atributos import ATRIBUTOS
from motosearch.validacion import COLUMNAS_FICHAS, normalizar, validar_fichas, verificar_cobertura

RAIZ = Path(__file__).resolve().parents[2]


def _fila(**kw):
    base = {
        "marca": "suzuki", "modelo": "DR150", "generacion": "2021-", "anio_modelo": "2026", "variante": "ABS",
        "estado": "vigente", "segmento": "doble-proposito", "atributo": "cilindrada", "valor_crudo": "149 cc",
        "fuente_tipo": "web_marca", "fuente_url": "https://www.suzuki.com.co/x", "fecha_consulta": "2026-11-13",
        "confianza": "alta", "notas": "",
    }
    base.update(kw)
    return base


def _csv(tmp_path, filas):
    p = tmp_path / "f.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS_FICHAS)
        w.writeheader()
        w.writerows(filas)
    return p


def test_fila_valida(tmp_path):
    r = validar_fichas(_csv(tmp_path, [_fila(), _fila(atributo="peso_orden_marcha", valor_crudo="134 kg")]))
    assert r.ok, r.errores
    assert r.filas_ok == 2


def test_cero_y_vacio_rechazados(tmp_path):
    r = validar_fichas(_csv(tmp_path, [_fila(valor_crudo=""), _fila(atributo="peso_seco", valor_crudo="0 kg")]))
    assert len(r.errores) == 2


def test_fuera_de_rango_detecta_error_de_parser():
    _, motivo = normalizar("cilindrada", "1490 cc ")
    assert motivo is None
    _, motivo = normalizar("peso_seco", "1340 kg")
    assert "máximo" in motivo


def test_enum_y_sin_fuente(tmp_path):
    r = validar_fichas(_csv(tmp_path, [_fila(atributo="abs", valor_crudo="doble canal", fuente_url="")]))
    assert any("no es un valor permitido" in e for e in r.errores)
    assert any("fuente_url" in e for e in r.errores)


def test_dos_segmentos_para_misma_version(tmp_path):
    r = validar_fichas(_csv(tmp_path, [_fila(), _fila(atributo="peso_seco", valor_crudo="120 kg", segmento="trabajo")]))
    assert any("dos segmentos" in e for e in r.errores)


def test_duplicado(tmp_path):
    r = validar_fichas(_csv(tmp_path, [_fila(), _fila()]))
    assert any("repetido" in e for e in r.errores)


def test_plantillas_vacias_son_validas():
    for nombre in ("fichas_fase0.csv", "descontinuadas.csv"):
        assert validar_fichas(RAIZ / "data" / "manual" / nombre).ok


def test_cobertura():
    assert verificar_cobertura(40, 50) is None
    assert "detenido" in verificar_cobertura(39, 50)
    assert verificar_cobertura(10, None) is None


def test_catalogo_python_coincide_con_seed_sql():
    sql = (RAIZ / "db" / "seed" / "0001_catalogos.sql").read_text(encoding="utf-8")
    bloque = sql.split("INSERT INTO atributo", 1)[1].split(";", 1)[0]
    claves_sql = set(re.findall(r"^\s*\('([a-z_]+)'", bloque, flags=re.MULTILINE))
    assert claves_sql == set(ATRIBUTOS)


def test_exportar_catalogo_real():
    from motosearch.exportar import catalogo_desde_seed, exportar

    atributos, segmentos = catalogo_desde_seed()
    assert atributos["peso_sin_especificar"]["rankeable"] is False
    assert atributos["potencia_max"]["nombre"] == "Potencia máxima"
    assert "naked" in segmentos
    d = exportar(RAIZ / "data" / "manual" / "fichas_fase0.csv", RAIZ / "data" / "manual" / "precios.csv")
    assert len(d["versiones"]) >= 20
    for v in d["versiones"]:
        for dato in v["specs"].values():
            assert dato["valor"] not in (0, None, "")
            assert dato["fuente_url"].startswith("http")


def test_json_de_la_web_esta_al_dia():
    """Si falla: corre `motosearch exportar` y haz commit de web/src/data/catalogo.json."""
    import json

    from motosearch.exportar import exportar

    ruta = RAIZ / "web" / "src" / "data" / "catalogo.json"
    d = exportar(RAIZ / "data" / "manual" / "fichas_fase0.csv", RAIZ / "data" / "manual" / "precios.csv")
    assert json.loads(ruta.read_text(encoding="utf-8")) == d
