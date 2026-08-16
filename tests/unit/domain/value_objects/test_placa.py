import dataclasses

import pytest

from domain.value_objects.placa import Placa


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("ABC1234", "ABC1234"),
        ("abc1234", "ABC1234"),
        ("ABC-1234", "ABC1234"),
        ("abc 1234", "ABC1234"),
        ("  abc-1234  ", "ABC1234"),
        ("ABC1D23", "ABC1D23"),
        ("abc1d23", "ABC1D23"),
    ],
)
def test_normalizacao(entrada, esperado):
    """Testa a remoção de máscara e a conversão para maiúsculas."""

    assert Placa(entrada).value == esperado


def test_sempre_sete_caracteres_maiusculos():
    """Testa o invariante central do value object."""

    placa = Placa("abc-1d23")

    assert len(placa.value) == 7
    assert placa.value.isupper()


def test_identifica_o_padrao():
    """Testa a distinção entre placa antiga e Mercosul."""

    assert Placa("ABC1234").is_mercosul is False
    assert Placa("ABC1234").padrao == "Antigo"
    assert Placa("ABC1D23").is_mercosul is True
    assert Placa("ABC1D23").padrao == "Mercosul"


def test_formatacao_para_exibicao():
    """Testa a máscara: hífen só no padrão antigo."""

    assert Placa("ABC1234").formatada() == "ABC-1234"
    assert Placa("ABC1D23").formatada() == "ABC1D23"


def test_igualdade_por_valor():
    """Testa que a mesma placa com máscaras diferentes é o mesmo valor."""

    assert Placa("abc-1234") == Placa("ABC1234")
    assert hash(Placa("abc-1234")) == hash(Placa("ABC1234"))
    assert len({Placa("abc 1234"), Placa("ABC1234")}) == 1


@pytest.mark.parametrize("entrada", [None, "", "   ", "---", 1234567])
def test_placa_obrigatoria(entrada):
    """Testa a rejeição de valores vazios ou de outro tipo."""

    with pytest.raises(ValueError):
        Placa(entrada)


@pytest.mark.parametrize("entrada", ["ABC123", "ABC12345", "AB1234"])
def test_quantidade_de_caracteres_invalida(entrada):
    """Testa a rejeição de placas que não têm 7 caracteres."""

    with pytest.raises(ValueError, match="exatamente 7 caracteres"):
        Placa(entrada)


@pytest.mark.parametrize(
    "entrada",
    ["1234ABC", "ABCDEFG", "1234567", "AB1C234", "ABCD123"],
)
def test_formato_invalido(entrada):
    """Testa a rejeição de placas com 7 caracteres fora do padrão."""

    with pytest.raises(ValueError, match="formato ABC1234"):
        Placa(entrada)


def test_e_imutavel():
    """Testa que a placa não pode ser alterada após a criação."""

    placa = Placa("ABC1234")

    with pytest.raises(dataclasses.FrozenInstanceError):
        placa.value = "XYZ9876"


def test_str_devolve_a_placa():
    """Testa a conversão para texto, usada na persistência."""

    assert str(Placa("abc-1234")) == "ABC1234"


def test_aceita_outra_instancia_de_placa():
    """Testa que uma Placa já validada é aceita diretamente."""

    original = Placa("ABC1234")
    assert Placa(original) == original
