import pytest

from motosearch.fetcher import Fetcher, FuenteNoAprobada
from motosearch.fuentes import cargar_fuentes


def test_registro_carga_y_cubre_las_11_marcas():
    fuentes = cargar_fuentes()
    marcas = {m for f in fuentes.values() for m in f.marcas}
    assert marcas == {"bajaj", "suzuki", "honda", "akt", "yamaha", "tvs", "hero", "victory",
                      "vento", "ktm", "royal-enfield"}


def test_fetcher_rechaza_fuente_no_aprobada(tmp_path):
    f = cargar_fuentes()["suzuki-co"]
    with pytest.raises(FuenteNoAprobada):
        Fetcher(f, tmp_path)
