from decimal import Decimal

import pytest

from domain.entities.servico import Servico
from domain.value_objects.dinheiro import Dinheiro


def criar_servico(**kwargs) -> Servico:
    padrao = {
        "nome": "Troca de óleo",
        "valor": Decimal("120.00"),
        "tempo_estimado": "1h",
    }
    padrao.update(kwargs)

    return Servico(**padrao)


def test_cria_servico_valido():
    """Testa a criação de um serviço com dados válidos."""

    servico = criar_servico(descricao="Inclui filtro")

    assert servico.id is None
    assert servico.nome == "Troca de óleo"
    assert servico.valor == Dinheiro("120.00")
    assert servico.tempo_estimado == "1h"
    assert servico.descricao == "Inclui filtro"


@pytest.mark.parametrize("nome", ["", "   ", None])
def test_nome_obrigatorio(nome):
    """Testa que o serviço não pode ser criado sem nome."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        criar_servico(nome=nome)


def test_nome_com_tamanho_excedido():
    """Testa o limite de 100 caracteres do nome."""

    with pytest.raises(ValueError, match="no máximo 100 caracteres"):
        criar_servico(nome="a" * 101)


def test_valor_obrigatorio():
    """Testa que o serviço não pode ser criado sem valor."""

    with pytest.raises(ValueError, match="deve ser preenchido"):
        criar_servico(valor=None)


def test_valor_negativo():
    """Testa que o valor do serviço não pode ser negativo."""

    with pytest.raises(ValueError, match="não pode ser negativo"):
        criar_servico(valor=Decimal("-0.01"))


def test_valor_zero_e_permitido():
    """Testa que um serviço de cortesia pode ter valor zero."""

    servico = criar_servico(valor=Decimal("0"))

    assert servico.valor == Dinheiro("0.00")


def test_valor_acima_do_limite_da_coluna():
    """Testa o teto imposto por NUMERIC(10,2)."""

    with pytest.raises(ValueError, match="não pode ultrapassar"):
        criar_servico(valor=Decimal("100000000.00"))


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        (Decimal("45.999"), Dinheiro("46.00")),
        (Decimal("45.994"), Dinheiro("45.99")),
        (Decimal("0.125"), Dinheiro("0.13")),
        (Decimal("10"), Dinheiro("10.00")),
    ],
)
def test_valor_e_arredondado_para_duas_casas(entrada, esperado):
    """Testa o arredondamento comercial para o formato da coluna."""

    servico = criar_servico(valor=entrada)

    assert servico.valor == esperado


def test_tempo_estimado_opcional():
    """Testa que o tempo estimado pode ficar em branco."""

    servico = criar_servico(tempo_estimado="   ")

    assert servico.tempo_estimado is None


def test_tempo_estimado_com_tamanho_excedido():
    """Testa o limite de 30 caracteres do tempo estimado."""

    with pytest.raises(ValueError, match="no máximo 30 caracteres"):
        criar_servico(tempo_estimado="a" * 31)


def test_change_valor_revalida():
    """Testa que a alteração de valor passa pelas mesmas regras."""

    servico = criar_servico()

    with pytest.raises(ValueError, match="não pode ser negativo"):
        servico.change_valor(Decimal("-1"))

    assert servico.valor == Dinheiro("120.00")


def test_change_nome():
    """Testa a alteração do nome do serviço."""

    servico = criar_servico()
    servico.change_nome("Alinhamento e balanceamento")

    assert servico.nome == "Alinhamento e balanceamento"


def test_change_descricao():
    """Testa a alteração da descrição do serviço."""

    servico = criar_servico()
    servico.change_descricao("  Detalhes  ")
    assert servico.descricao == "Detalhes"

    servico.change_descricao(None)
    assert servico.descricao is None


def test_change_tempo_estimado():
    """Testa a alteração do tempo estimado do serviço."""

    servico = criar_servico()
    servico.change_tempo_estimado("2h")

    assert servico.tempo_estimado == "2h"
