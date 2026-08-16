from unittest.mock import AsyncMock

import pytest

from application.commands.adicionar_insumo_ordem_servico import (
    AdicionarInsumoOrdemServicoCommand,
    AdicionarInsumoOrdemServicoUseCase,
    InsumoNaoEncontradoError,
)
from domain.entities.insumo import Insumo
from domain.entities.ordem_servico import OrdemServico


def _use_case(**overrides):
    repos = dict(ordem_servico_repository=AsyncMock(), insumo_repository=AsyncMock())
    repos.update(overrides)
    return AdicionarInsumoOrdemServicoUseCase(**repos), repos


@pytest.mark.asyncio
async def test_adiciona_insumo_com_sucesso_e_debita_estoque():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    insumo = Insumo(id=10, nome="Óleo 5W30", preco_unitario="45.90", estoque=10)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = lambda o: o
    repos["insumo_repository"].find_by_id.return_value = insumo
    repos["insumo_repository"].update.side_effect = lambda i: i

    resultado = await use_case.execute(
        AdicionarInsumoOrdemServicoCommand(
            ordem_servico_id=1, insumo_id=10, quantidade=2
        )
    )

    assert len(resultado.insumos_utilizados) == 1
    item = resultado.insumos_utilizados[0]
    assert item["insumo_id"] == "10"
    assert item["valor"] == 45.90
    assert item["quantidade"] == 2

    assert insumo.estoque == 8  # 10 - 2
    repos["insumo_repository"].update.assert_awaited_once_with(insumo)
    repos["ordem_servico_repository"].save.assert_awaited_once_with(ordem)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = None

    resultado = await use_case.execute(
        AdicionarInsumoOrdemServicoCommand(ordem_servico_id=999, insumo_id=10)
    )

    assert resultado is None
    repos["insumo_repository"].find_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_insumo_nao_encontrado():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["insumo_repository"].find_by_id.return_value = None

    with pytest.raises(InsumoNaoEncontradoError, match="999"):
        await use_case.execute(
            AdicionarInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=999)
        )

    repos["ordem_servico_repository"].save.assert_not_called()


@pytest.mark.asyncio
async def test_falha_quando_estoque_insuficiente():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    insumo = Insumo(id=10, nome="Óleo 5W30", estoque=1)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["insumo_repository"].find_by_id.return_value = insumo

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        await use_case.execute(
            AdicionarInsumoOrdemServicoCommand(
                ordem_servico_id=1, insumo_id=10, quantidade=5
            )
        )

    repos["insumo_repository"].update.assert_not_called()
    repos["ordem_servico_repository"].save.assert_not_called()


@pytest.mark.asyncio
async def test_insumo_sem_preco_unitario_usa_valor_zero():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    insumo = Insumo(id=10, nome="Insumo sem preço", estoque=5)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = lambda o: o
    repos["insumo_repository"].find_by_id.return_value = insumo
    repos["insumo_repository"].update.side_effect = lambda i: i

    resultado = await use_case.execute(
        AdicionarInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=10)
    )

    assert resultado.insumos_utilizados[0]["valor"] == 0.0
