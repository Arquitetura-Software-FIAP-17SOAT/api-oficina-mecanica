from unittest.mock import AsyncMock

import pytest

from application.commands.enviar_ordem_servico_para_aprovacao import (
    EnviarOrdemServicoParaAprovacaoCommand,
    EnviarOrdemServicoParaAprovacaoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_em_diagnostico() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    return ordem


@pytest.mark.asyncio
async def test_envia_para_aprovacao_com_sucesso():
    ordem = _ordem_em_diagnostico()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = EnviarOrdemServicoParaAprovacaoUseCase(mock_repository)
    resultado = await use_case.execute(
        EnviarOrdemServicoParaAprovacaoCommand(
            ordem_servico_id=1, orcamento=250.0, observacoes="Orçamento enviado"
        )
    )

    assert resultado.status == StatusOrdemServico.AGUARDANDO_APROVACAO
    assert resultado.orcamento == 250.0
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = EnviarOrdemServicoParaAprovacaoUseCase(mock_repository)
    resultado = await use_case.execute(
        EnviarOrdemServicoParaAprovacaoCommand(ordem_servico_id=999, orcamento=100.0)
    )

    assert resultado is None
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_com_orcamento_nao_positivo():
    ordem = _ordem_em_diagnostico()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = EnviarOrdemServicoParaAprovacaoUseCase(mock_repository)

    with pytest.raises(ValueError, match="positivo"):
        await use_case.execute(
            EnviarOrdemServicoParaAprovacaoCommand(ordem_servico_id=1, orcamento=0)
        )

    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_gera_orcamento_automaticamente_quando_nao_informado():
    """Comando sem orçamento deve usar o total calculado dos itens da OS."""
    ordem = _ordem_em_diagnostico()
    ordem.adicionar_item("10", 150.0, quantidade=2)

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = EnviarOrdemServicoParaAprovacaoUseCase(mock_repository)
    resultado = await use_case.execute(
        EnviarOrdemServicoParaAprovacaoCommand(ordem_servico_id=1)
    )

    assert resultado.status == StatusOrdemServico.AGUARDANDO_APROVACAO
    assert resultado.orcamento == 300.0
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_falha_ao_gerar_orcamento_automatico_sem_itens():
    """Sem serviços na OS, o orçamento automático não pode ser gerado."""
    ordem = _ordem_em_diagnostico()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = EnviarOrdemServicoParaAprovacaoUseCase(mock_repository)

    with pytest.raises(ValueError, match="não possui serviços adicionados"):
        await use_case.execute(
            EnviarOrdemServicoParaAprovacaoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()
