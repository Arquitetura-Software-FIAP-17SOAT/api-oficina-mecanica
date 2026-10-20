import pytest

from adapters.database.database import engine, ler_booleano


@pytest.mark.parametrize("valor", ["true", "TRUE", "1", "yes", "on", " True "])
def test_ler_booleano_aceita_valores_verdadeiros(monkeypatch, valor):
    monkeypatch.setenv("FLAG_TESTE", valor)

    assert ler_booleano("FLAG_TESTE") is True


@pytest.mark.parametrize("valor", ["false", "0", "no", "off", "", "qualquer"])
def test_ler_booleano_trata_o_resto_como_falso(monkeypatch, valor):
    monkeypatch.setenv("FLAG_TESTE", valor)

    assert ler_booleano("FLAG_TESTE") is False


def test_ler_booleano_usa_o_padrao_quando_a_variavel_nao_existe(monkeypatch):
    monkeypatch.delenv("FLAG_TESTE", raising=False)

    assert ler_booleano("FLAG_TESTE") is False
    assert ler_booleano("FLAG_TESTE", padrao=True) is True


def test_o_engine_nao_imprime_sql_por_padrao():
    assert engine.echo is False
