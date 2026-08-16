from unittest.mock import AsyncMock

import pytest

from application.commands.remover_item_ordem_servico import (
    RemoverItemOrdemServicoCommand,
    RemoverItemOrdemServicoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_com_item() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.adicionar_item("10", 120.00)
    return ordem


@pytest.mark.asyncio
async def test_remove_item_com_sucesso():
    ordem = _ordem_com_item()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = RemoverItemOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        RemoverItemOrdemServicoCommand(ordem_servico_id=1, servico_id="10")
    )

    assert resultado.itens == []
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = RemoverItemOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        RemoverItemOrdemServicoCommand(ordem_servico_id=999, servico_id="10")
    )

    assert resultado is None


@pytest.mark.asyncio
async def test_falha_quando_item_nao_esta_na_ordem():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = RemoverItemOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="não encontrado"):
        await use_case.execute(
            RemoverItemOrdemServicoCommand(ordem_servico_id=1, servico_id="999")
        )

    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_os_ja_foi_finalizada():
    ordem = _ordem_com_item()
    ordem.status = StatusOrdemServico.FINALIZADA

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = RemoverItemOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Finalizada"):
        await use_case.execute(
            RemoverItemOrdemServicoCommand(ordem_servico_id=1, servico_id="10")
        )

    mock_repository.save.assert_not_called()
