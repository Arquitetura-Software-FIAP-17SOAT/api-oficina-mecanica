import pytest

from domain.value_objects.descricao import Descricao


def test_cria_descricao_valida():
    descricao = Descricao("Troca de óleo e filtro")

    assert str(descricao) == "Troca de óleo e filtro"


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_descricao_vazia_e_invalida(valor):
    with pytest.raises(ValueError, match="não pode ser vazia"):
        Descricao(valor)


def test_descricao_muito_curta_e_invalida():
    with pytest.raises(ValueError, match="mínimo"):
        Descricao("ab")


def test_descricao_muito_longa_e_invalida():
    with pytest.raises(ValueError, match="exceder"):
        Descricao("a" * 1001)


def test_descricao_e_igual_por_valor():
    assert Descricao("Troca de óleo") == Descricao("Troca de óleo")
    assert Descricao("Troca de óleo") != Descricao("Alinhamento")
    assert Descricao("Troca de óleo") != "Troca de óleo"


def test_descricao_repr():
    assert repr(Descricao("Troca de óleo")) == "Descricao('Troca de óleo')"
