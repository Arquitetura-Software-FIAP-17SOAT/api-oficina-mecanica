from unittest.mock import AsyncMock

import pytest

from application.commands.rejeitar_orcamento_ordem_servico import (
    RejeitarOrcamentoOrdemServicoCommand,
    RejeitarOrcamentoOrdemServicoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_orcamento import StatusOrcamento
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_aguardando_aprovacao() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)
    return ordem


@pytest.mark.asyncio
async def test_rejeitar_orcamento_finaliza_ordem_e_registra_historico():
    ordem = _ordem_aguardando_aprovacao()
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda ordem_servico: ordem_servico

    use_case = RejeitarOrcamentoOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        RejeitarOrcamentoOrdemServicoCommand(ordem_servico_id=1)
    )

    assert resultado.status_orcamento == StatusOrcamento.REJEITADO
    assert resultado.status == StatusOrdemServico.FINALIZADA
    assert resultado.historico_status[-1]["status"] == StatusOrdemServico.FINALIZADA
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_rejeitar_orcamento_falha_fora_de_aguardando_aprovacao():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = RejeitarOrcamentoOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Não é possível rejeitar"):
        await use_case.execute(
            RejeitarOrcamentoOrdemServicoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_rejeitar_orcamento_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = RejeitarOrcamentoOrdemServicoUseCase(mock_repository)

    assert await use_case.execute(
        RejeitarOrcamentoOrdemServicoCommand(ordem_servico_id=999)
    ) is None
    mock_repository.save.assert_not_called()