from unittest.mock import AsyncMock

import pytest

from application.commands.iniciar_diagnostico_ordem_servico import (
    IniciarDiagnosticoOrdemServicoCommand,
    IniciarDiagnosticoOrdemServicoUseCase,
)
from domain.entities.ordem_servico import OrdemServico
from domain.value_objects.status_ordem_servico import StatusOrdemServico


@pytest.mark.asyncio
async def test_inicia_diagnostico_com_sucesso():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem
    mock_repository.save.side_effect = lambda o: o

    use_case = IniciarDiagnosticoOrdemServicoUseCase(mock_repository)
    command = IniciarDiagnosticoOrdemServicoCommand(
        ordem_servico_id=1, observacoes="Verificando motor"
    )

    resultado = await use_case.execute(command)

    assert resultado.status == StatusOrdemServico.EM_DIAGNOSTICO
    assert resultado.observacoes == "Verificando motor"
    mock_repository.save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = None

    use_case = IniciarDiagnosticoOrdemServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        IniciarDiagnosticoOrdemServicoCommand(ordem_servico_id=999)
    )

    assert resultado is None
    mock_repository.save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_transicao_invalida():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.iniciar_diagnostico()  # já está em diagnóstico

    mock_repository = AsyncMock()
    mock_repository.find_by_id.return_value = ordem

    use_case = IniciarDiagnosticoOrdemServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Não é possível transicionar"):
        await use_case.execute(
            IniciarDiagnosticoOrdemServicoCommand(ordem_servico_id=1)
        )

    mock_repository.save.assert_not_called()
