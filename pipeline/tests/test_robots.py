from motosearch.robots import Robots

UA = "motosearch-bot/0.1"

AUTECO = """
User-agent: *
Disallow: /img/*
Disallow: /busca/*
User-agent: *
Allow: /*.css
Disallow: /*?
Allow: /*?page=
Disallow: *returnUrl*
Allow: /api/catalog_system/
User-agent: *
Disallow: /*skuId=
Allow: /*idsku=
"""


def test_auteco_url_limpia_permitida():
    r = Robots(AUTECO)
    assert r.permitido("https://www.auteco.com.co/tvs-apache-rtr-160/p", UA)


def test_auteco_parametros_prohibidos_salvo_page():
    r = Robots(AUTECO)
    assert not r.permitido("https://www.auteco.com.co/motos?color=rojo", UA)
    assert r.permitido("https://www.auteco.com.co/motos?page=2", UA)
    assert not r.permitido("https://www.auteco.com.co/busca/apache", UA)
    assert not r.permitido("https://www.auteco.com.co/x?returnUrl=/a", UA)


def test_auteco_api_catalogo_permitida():
    r = Robots(AUTECO)
    assert r.permitido("https://www.auteco.com.co/api/catalog_system/pub/products/search", UA)


def test_ancla_dolar():
    r = Robots("User-agent: *\nDisallow: /login$\n")
    assert not r.permitido("https://x.co/login", UA)
    assert r.permitido("https://x.co/login/ayuda", UA)


def test_grupo_especifico_gana():
    r = Robots("User-agent: *\nDisallow: /\n\nUser-agent: motosearch-bot\nAllow: /\n")
    assert r.permitido("https://x.co/a", UA)
    assert not r.permitido("https://x.co/a", "otro-bot")


def test_vacio_permite_todo():
    assert Robots("").permitido("https://x.co/cualquier", UA)
