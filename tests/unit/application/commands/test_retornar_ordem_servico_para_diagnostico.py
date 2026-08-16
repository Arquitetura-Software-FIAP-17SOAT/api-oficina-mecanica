from unittest.mock import AsyncMock

import pytest

from application.commands.retornar_ordem_servico_para_diagnostico import (
    RetornarOrdemServicoParaDiagnosticoCommand,
    RetornarOrdemServicoParaDiagnosticoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


def _ordem_aguardando_aprovacao() -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()
    ordem.enviar_para_aprovacao(orcamento=250.0)
    return ordem


@pytest.mark.asyncio
async def test_retorna_ordem_para_diagnostico_com_sucesso():
    ordem = _ordem_aguardando_aprovacao()

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = RetornarOrdemServicoParaDiagnosticoUseCase(mock_repository)
    resultado = await use_case.execute(
        RetornarOrdemServicoParaDiagnosticoCommand(
            ordem_servico_id=1, motivo="Cliente pediu revisão do orçamento"
        )
    )

    assert resultado.status == StatusOrdemServico.EM_DIAGNOSTICO
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = RetornarOrdemServicoParaDiagnosticoUseCase(mock_repository)
    resultado = await use_case.execute(
        RetornarOrdemServicoParaDiagnosticoCommand(ordem_servico_id=999)
    )

    assert resultado is None
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_ao_retornar_de_status_invalido():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = RetornarOrdemServicoParaDiagnosticoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Não é possível retornar"):
        await use_case.execute(
            RetornarOrdemServicoParaDiagnosticoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()
