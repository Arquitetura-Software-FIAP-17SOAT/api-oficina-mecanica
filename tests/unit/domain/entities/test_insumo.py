from decimal import Decimal

import pytest

from domain.entities.insumo import Insumo
from domain.value_objects.dinheiro import Dinheiro


def criar_insumo(**kwargs) -> Insumo:
    padrao = {
        "nome": "Óleo 5W30",
        "preco_unitario": Decimal("45.90"),
        "estoque": 10,
        "quantidade_minima": 3,
    }
    padrao.update(kwargs)

    return Insumo(**padrao)


def test_cria_insumo_valido():
    """Testa a criação de um insumo com dados válidos."""

    insumo = criar_insumo()

    assert insumo.id is None
    assert insumo.nome == "Óleo 5W30"
    assert insumo.preco_unitario == Dinheiro("45.90")
    assert insumo.estoque == 10
    assert insumo.quantidade_minima == 3


def test_nome_e_normalizado():
    """Testa que espaços em volta do nome são removidos."""

    insumo = criar_insumo(nome="  Filtro de ar  ")

    assert insumo.nome == "Filtro de ar"


@pytest.mark.parametrize("nome", ["", "   ", None])
def test_nome_obrigatorio(nome):
    """Testa que o insumo não pode ser criado sem nome."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        criar_insumo(nome=nome)


def test_nome_com_tamanho_excedido():
    """Testa o limite de 120 caracteres do nome."""

    with pytest.raises(ValueError, match="no máximo 120 caracteres"):
        criar_insumo(nome="a" * 121)


def test_preco_unitario_negativo():
    """Testa que o preço unitário não pode ser negativo."""

    with pytest.raises(ValueError, match="não pode ser negativo"):
        criar_insumo(preco_unitario=Decimal("-1.00"))


def test_preco_unitario_opcional():
    """Testa que o insumo pode ser criado sem preço."""

    insumo = criar_insumo(preco_unitario=None)

    assert insumo.preco_unitario is None


def test_estoque_inicial_negativo():
    """Testa que o estoque inicial não pode ser negativo."""

    with pytest.raises(ValueError, match="não pode ser negativo"):
        criar_insumo(estoque=-1)


def test_adicionar_estoque():
    """Testa a entrada de estoque."""

    insumo = criar_insumo(estoque=10)

    insumo.adicionar_estoque(5)

    assert insumo.estoque == 15


def test_remover_estoque():
    """Testa a saída de estoque dentro do saldo disponível."""

    insumo = criar_insumo(estoque=10)

    insumo.remover_estoque(4)

    assert insumo.estoque == 6


def test_remover_estoque_ate_zerar():
    """Testa que é possível consumir todo o saldo."""

    insumo = criar_insumo(estoque=10)

    insumo.remover_estoque(10)

    assert insumo.estoque == 0


def test_remover_estoque_insuficiente():
    """Testa que a saída não pode deixar o saldo negativo."""

    insumo = criar_insumo(estoque=3)

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        insumo.remover_estoque(4)

    assert insumo.estoque == 3


@pytest.mark.parametrize("quantidade", [0, -5])
def test_movimentacao_exige_quantidade_positiva(quantidade):
    """Testa que entrada e saída exigem quantidade maior que zero."""

    insumo = criar_insumo()

    with pytest.raises(ValueError, match="maior que zero"):
        insumo.adicionar_estoque(quantidade)

    with pytest.raises(ValueError, match="maior que zero"):
        insumo.remover_estoque(quantidade)


def test_ajustar_estoque_define_saldo_absoluto():
    """Testa o ajuste de inventário."""

    insumo = criar_insumo(estoque=10)

    insumo.ajustar_estoque(7)

    assert insumo.estoque == 7


def test_ajustar_estoque_aceita_zero():
    """Testa que a contagem física pode zerar o saldo."""

    insumo = criar_insumo(estoque=10)

    insumo.ajustar_estoque(0)

    assert insumo.estoque == 0


def test_ajustar_estoque_nao_aceita_negativo():
    """Testa que o ajuste não pode deixar o saldo negativo."""

    insumo = criar_insumo(estoque=10)

    with pytest.raises(ValueError, match="não pode ser negativo"):
        insumo.ajustar_estoque(-1)


@pytest.mark.parametrize(
    "estoque,quantidade_minima,esperado",
    [
        (10, 3, False),
        (4, 3, False),
        (3, 3, True),
        (2, 3, True),
        (0, 0, True),
    ],
)
def test_estoque_baixo(estoque, quantidade_minima, esperado):
    """Testa o alerta de reposição no limite da quantidade mínima."""

    insumo = criar_insumo(estoque=estoque, quantidade_minima=quantidade_minima)

    assert insumo.estoque_baixo is esperado


def test_movimentacao_com_quantidade_nao_inteira_e_invalida():
    """Testa que a movimentação de estoque exige um inteiro."""

    insumo = criar_insumo()

    with pytest.raises(ValueError, match="número inteiro"):
        insumo.adicionar_estoque(1.5)


def test_quantidade_nao_inteira_e_invalida():
    """Testa que estoque/quantidade mínima exigem um inteiro."""

    with pytest.raises(ValueError, match="número inteiro"):
        criar_insumo(estoque=1.5)


def test_change_nome():
    """Testa a alteração do nome do insumo."""

    insumo = criar_insumo()
    insumo.change_nome("Óleo 5W40")

    assert insumo.nome == "Óleo 5W40"


def test_change_descricao():
    """Testa a alteração da descrição do insumo."""

    insumo = criar_insumo()
    insumo.change_descricao("  Nova descrição  ")
    assert insumo.descricao == "Nova descrição"

    insumo.change_descricao(None)
    assert insumo.descricao is None


def test_change_preco_unitario():
    """Testa a alteração do preço unitário do insumo."""

    insumo = criar_insumo()
    insumo.change_preco_unitario(Decimal("99.90"))

    assert insumo.preco_unitario == Dinheiro("99.90")

    insumo.change_preco_unitario(None)
    assert insumo.preco_unitario is None


def test_change_quantidade_minima():
    """Testa a alteração da quantidade mínima do insumo."""

    insumo = criar_insumo()
    insumo.change_quantidade_minima(7)

    assert insumo.quantidade_minima == 7
