import pytest

from motosearch.units import (
    consumo_a_km_gal,
    longitud_a_mm,
    parse_numero,
    potencia_a_hp,
    torque_a_nm,
)


@pytest.mark.parametrize("txt,esperado", [
    ("17,2", 17.2), ("8.500", 8500), ("1.234,5", 1234.5), ("17.2", 17.2), ("155 cc", 155),
    ("sin dato", None),
])
def test_parse_numero(txt, esperado):
    assert parse_numero(txt) == esperado


def test_potencia_ps_a_hp_con_rpm():
    hp, v = potencia_a_hp("15,4 PS @ 8.500 rpm")
    assert hp == pytest.approx(15.19, abs=0.01)
    assert v.a_rpm == 8500 and v.unidad_original == "ps"


def test_potencia_kw():
    hp, _ = potencia_a_hp("11 kW a 9000 rpm")
    assert hp == pytest.approx(14.75, abs=0.01)


def test_potencia_sin_unidad_no_adivina():
    assert potencia_a_hp("17") is None


def test_torque_kgfm():
    nm, v = torque_a_nm("1,4 kgf·m @ 7.000 rpm")
    assert nm == pytest.approx(13.73, abs=0.01)
    assert v.a_rpm == 7000


def test_consumo_km_l_a_km_gal():
    assert consumo_a_km_gal("40 km/l") == pytest.approx(151.4, abs=0.1)
    assert consumo_a_km_gal("120 km/gal") == 120
    assert consumo_a_km_gal("120") is None


def test_longitud():
    assert longitud_a_mm("790 mm") == 790
    assert longitud_a_mm("79 cm") == 790
