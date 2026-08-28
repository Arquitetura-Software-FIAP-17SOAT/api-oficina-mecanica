from unittest.mock import AsyncMock

import pytest

from application.commands.aprovar_orcamento_ordem_servico import (
    AprovarOrcamentoOrdemServicoCommand,
    AprovarOrcamentoOrdemServicoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_orcamento import StatusOrcamento
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_aguardando_aprovacao_com_item() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)
    ordem.adicionar_item("10", 250.0)
    return ordem


@pytest.mark.asyncio
async def test_evento_de_aprovacao_do_cliente_move_para_em_execucao():
    """Simula o gatilho externo: o cliente aprovou o orçamento pelo app."""
    ordem = _ordem_aguardando_aprovacao_com_item()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = AprovarOrcamentoOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=1)
    )

    mock_repository.find_by_id.assert_awaited_once_with(1)
    assert resultado.status_orcamento == StatusOrcamento.APROVADO
    assert resultado.status == StatusOrdemServico.EM_EXECUCAO
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = AprovarOrcamentoOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=999)
    )

    assert resultado is None
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_aprovar_sem_itens_cadastrados():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = AprovarOrcamentoOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="pelo menos um serviço"):
        await use_case.execute(
            AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_aprovar_ordem_ainda_recebida():
    """Não deve permitir pular direto de 'Recebida' para 'Em execução'."""
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = AprovarOrcamentoOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Não é possível transicionar"):
        await use_case.execute(
            AprovarOrcamentoOrdemServicoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()
