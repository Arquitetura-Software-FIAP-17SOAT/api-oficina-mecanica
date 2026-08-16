from unittest.mock import AsyncMock

import pytest

from application.commands.entregar_ordem_servico import (
    EntregarOrdemServicoCommand,
    EntregarOrdemServicoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_finalizada() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)
    ordem.adicionar_item("10", 250.0)
    ordem.aprovar_e_iniciar_execucao()
    ordem.finalizar()
    return ordem


@pytest.mark.asyncio
async def test_entrega_ordem_com_sucesso():
    ordem = _ordem_finalizada()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = EntregarOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        EntregarOrdemServicoCommand(ordem_servico_id=1, observacoes="Entregue")
    )

    assert resultado.status == StatusOrdemServico.ENTREGUE
    assert resultado.observacoes == "Entregue"
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = EntregarOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        EntregarOrdemServicoCommand(ordem_servico_id=999)
    )

    assert resultado is None
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_entregar_ordem_ainda_em_execucao():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)
    ordem.adicionar_item("10", 250.0)
    ordem.aprovar_e_iniciar_execucao()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = EntregarOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Não é possível transicionar"):
        await use_case.execute(EntregarOrdemServicoCommand(ordem_servico_id=1))

    mock_repository.save.assert_not_called()
