import dataclasses
from decimal import Decimal

import pytest

from domain.value_objects.dinheiro import Dinheiro


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        (Decimal("45.90"), "45.90"),
        ("45.90", "45.90"),
        (45.90, "45.90"),
        (45, "45.00"),
        (0, "0.00"),
    ],
)
def test_aceita_diferentes_entradas(entrada, esperado):
    """Testa a criação a partir de Decimal, string, float e int."""

    assert str(Dinheiro(entrada)) == esperado


def test_float_nao_contamina_o_valor():
    """Testa que o float é convertido via string, sem erro binário."""

    assert Dinheiro(0.1).value == Decimal("0.10")
    assert Dinheiro(0.1) + Dinheiro(0.2) == Dinheiro("0.30")


def test_soma_de_parcelas_nao_acumula_erro():
    """Testa dez parcelas que em float dariam 189.00000000000003."""

    total = Dinheiro.zero()

    for _ in range(10):
        total = total + Dinheiro("18.90")

    assert total == Dinheiro("189.00")


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        (Decimal("45.999"), "46.00"),
        (Decimal("45.994"), "45.99"),
        (Decimal("0.125"), "0.13"),
    ],
)
def test_arredondamento_comercial(entrada, esperado):
    """Testa o arredondamento para duas casas."""

    assert str(Dinheiro(entrada)) == esperado


def test_igualdade_por_valor():
    """Testa que a mesma quantia é o mesmo valor."""

    assert Dinheiro("45.90") == Dinheiro(45.90)
    assert hash(Dinheiro("45.90")) == hash(Dinheiro(45.90))
    assert len({Dinheiro("45.90"), Dinheiro(45.90)}) == 1


def test_comparacao():
    """Testa a ordenação entre valores."""

    assert Dinheiro("10.00") < Dinheiro("10.01")
    assert Dinheiro("99.99") > Dinheiro("1.00")
    assert max(Dinheiro("5.00"), Dinheiro("7.50")) == Dinheiro("7.50")


def test_multiplicacao_por_quantidade():
    """Testa o cálculo de subtotal."""

    assert Dinheiro("18.90") * 10 == Dinheiro("189.00")
    assert 3 * Dinheiro("10.50") == Dinheiro("31.50")


def test_subtracao():
    """Testa a diferença entre valores."""

    assert Dinheiro("50.00") - Dinheiro("18.90") == Dinheiro("31.10")


def test_subtracao_nao_pode_ficar_negativa():
    """Testa que o invariante de não-negatividade vale na aritmética."""

    with pytest.raises(ValueError, match="não pode ser negativo"):
        Dinheiro("10.00") - Dinheiro("10.01")


def test_e_imutavel():
    """Testa que o valor não pode ser alterado após a criação."""

    valor = Dinheiro("45.90")

    with pytest.raises(dataclasses.FrozenInstanceError):
        valor.value = Decimal("1.00")


def test_valor_negativo():
    """Testa a rejeição de valores negativos."""

    with pytest.raises(ValueError, match="não pode ser negativo"):
        Dinheiro("-0.01")


def test_valor_acima_do_limite_da_coluna():
    """Testa o teto imposto por NUMERIC(10,2)."""

    with pytest.raises(ValueError, match="não pode ultrapassar"):
        Dinheiro("100000000.00")


@pytest.mark.parametrize("entrada", [None, "abc", "", float("nan"), float("inf")])
def test_entradas_invalidas(entrada):
    """Testa a rejeição de entradas que não são números."""

    with pytest.raises(ValueError):
        Dinheiro(entrada)


def test_is_zero():
    """Testa a checagem de valor zerado."""

    assert Dinheiro.zero().is_zero is True
    assert Dinheiro("0.01").is_zero is False


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("45.90", "R$ 45,90"),
        ("1234.50", "R$ 1.234,50"),
        ("1234567.89", "R$ 1.234.567,89"),
        ("0", "R$ 0,00"),
    ],
)
def test_formatacao_brasileira(entrada, esperado):
    """Testa a máscara de exibição em reais."""

    assert Dinheiro(entrada).formatado() == esperado
