import dataclasses

import pytest

from domain.value_objects.chassi import Chassi

CHASSI_VALIDO = "9BWZZZ377VT004251"


@pytest.mark.parametrize(
    "entrada",
    [
        CHASSI_VALIDO,
        CHASSI_VALIDO.lower(),
        f"  {CHASSI_VALIDO}  ",
        "9BW ZZZ 377 VT004251",
        "9BW-ZZZ-377-VT004251",
    ],
)
def test_normalizacao(entrada):
    """Testa a remoção de separadores e a conversão para maiúsculas."""

    assert Chassi(entrada).value == CHASSI_VALIDO


def test_sempre_dezessete_caracteres_maiusculos():
    """Testa o invariante central do value object."""

    chassi = Chassi(CHASSI_VALIDO.lower())

    assert len(chassi.value) == 17
    assert chassi.value.isupper()


def test_secoes_do_vin():
    """Testa a decomposição nas três seções do padrão ISO 3779."""

    chassi = Chassi(CHASSI_VALIDO)

    assert chassi.wmi == "9BW"
    assert chassi.vds == "ZZZ377"
    assert chassi.vis == "VT004251"
    assert chassi.wmi + chassi.vds + chassi.vis == CHASSI_VALIDO


def test_igualdade_por_valor():
    """Testa que o mesmo chassi com máscaras diferentes é o mesmo valor."""

    assert Chassi(CHASSI_VALIDO.lower()) == Chassi(CHASSI_VALIDO)
    assert hash(Chassi(f" {CHASSI_VALIDO} ")) == hash(Chassi(CHASSI_VALIDO))
    assert len({Chassi(CHASSI_VALIDO.lower()), Chassi(CHASSI_VALIDO)}) == 1


@pytest.mark.parametrize("entrada", [None, "", "   ", "---", 12345678901234567])
def test_chassi_obrigatorio(entrada):
    """Testa a rejeição de valores vazios ou de outro tipo."""

    with pytest.raises(ValueError):
        Chassi(entrada)


@pytest.mark.parametrize(
    "entrada",
    ["9BWZZZ377VT00425", "9BWZZZ377VT0042510", "ABC123"],
)
def test_quantidade_de_caracteres_invalida(entrada):
    """Testa a rejeição de chassi que não tem exatamente 17 caracteres."""

    with pytest.raises(ValueError, match="exatamente 17 caracteres"):
        Chassi(entrada)


@pytest.mark.parametrize("letra", ["I", "O", "Q"])
def test_rejeita_letras_proibidas(letra):
    """Testa as letras excluídas do padrão VIN para evitar ambiguidade."""

    entrada = letra + CHASSI_VALIDO[1:]

    with pytest.raises(ValueError, match="I, O ou Q"):
        Chassi(entrada)


def test_e_imutavel():
    """Testa que o chassi não pode ser alterado após a criação."""

    chassi = Chassi(CHASSI_VALIDO)

    with pytest.raises(dataclasses.FrozenInstanceError):
        chassi.value = "9BWZZZ377VT004252"


def test_str_devolve_o_chassi():
    """Testa a conversão para texto, usada na persistência."""

    assert str(Chassi(CHASSI_VALIDO.lower())) == CHASSI_VALIDO
