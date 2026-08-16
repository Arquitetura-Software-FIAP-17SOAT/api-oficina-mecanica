from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.commands.adicionar_item_ordem_servico import (
    AdicionarItemOrdemServicoCommand,
    AdicionarItemOrdemServicoUseCase,
    ServicoNaoEncontradoError,
)
from domain.entities.ordem_servico import OrdemServico
from domain.entities.servico import Servico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _use_case(**overrides):
    repos = dict(ordem_servico_repository=AsyncMock(), servico_repository=AsyncMock())
    repos.update(overrides)
    return AdicionarItemOrdemServicoUseCase(**repos), repos


@pytest.mark.asyncio
async def test_adiciona_item_com_sucesso():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    servico = Servico(id=10, nome="Troca de óleo", valor=Decimal("120.00"))

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = lambda o: o
    repos["servico_repository"].find_by_id.return_value = servico

    resultado = await use_case.execute(
        AdicionarItemOrdemServicoCommand(
            ordem_servico_id=1, servico_id="10", quantidade=2
        )
    )

    assert len(resultado.itens) == 1
    item = resultado.itens[0]
    assert item["servico_id"] == "10"
    assert item["valor"] == 120.00
    assert item["quantidade"] == 2
    repos["ordem_servico_repository"].save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = None

    resultado = await use_case.execute(
        AdicionarItemOrdemServicoCommand(ordem_servico_id=999, servico_id="10")
    )

    assert resultado is None
    repos["servico_repository"].find_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_servico_nao_encontrado():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["servico_repository"].find_by_id.return_value = None

    with pytest.raises(ServicoNaoEncontradoError, match="999"):
        await use_case.execute(
            AdicionarItemOrdemServicoCommand(ordem_servico_id=1, servico_id="999")
        )

    repos["ordem_servico_repository"].save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_os_ja_foi_entregue():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.status = StatusOrdemServico.ENTREGUE
    servico = Servico(id=10, nome="Troca de óleo", valor=Decimal("120.00"))

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["servico_repository"].find_by_id.return_value = servico

    with pytest.raises(ValueError, match="Entregue"):
        await use_case.execute(
            AdicionarItemOrdemServicoCommand(ordem_servico_id=1, servico_id="10")
        )

    repos["ordem_servico_repository"].save.assert_not_called()
