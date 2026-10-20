from unittest.mock import AsyncMock

import pytest

from application.commands.remover_insumo_ordem_servico import (
    RemoverInsumoOrdemServicoCommand,
    RemoverInsumoOrdemServicoUseCase,
)
from domain.entities.insumo import Insumo
from domain.entities.ordem_servico import OrdemServico
from tests.unit.fakes import UnitOfWorkFalso


def _use_case(**overrides):
    repos = dict(
        ordem_servico_repository=AsyncMock(),
        insumo_repository=AsyncMock(),
        unit_of_work=UnitOfWorkFalso(),
    )
    repos.update(overrides)
    return RemoverInsumoOrdemServicoUseCase(**repos), repos


def _ordem_com_insumo(quantidade: int = 3) -> OrdemServico:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.adicionar_insumo("10", 45.90, quantidade=quantidade)
    return ordem


@pytest.mark.asyncio
async def test_remove_insumo_e_estorna_estoque():
    ordem = _ordem_com_insumo(quantidade=3)
    insumo = Insumo(id=10, nome="Óleo 5W30", estoque=7)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = lambda o: o
    repos["insumo_repository"].find_by_id.return_value = insumo
    repos["insumo_repository"].update.side_effect = lambda i: i

    resultado = await use_case.execute(
        RemoverInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=10)
    )

    assert resultado.insumos_utilizados == []
    assert insumo.estoque == 10  # 7 + 3 estornado
    repos["insumo_repository"].update.assert_awaited_once_with(insumo)


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_encontrada():
    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = None

    resultado = await use_case.execute(
        RemoverInsumoOrdemServicoCommand(ordem_servico_id=999, insumo_id=10)
    )

    assert resultado is None


@pytest.mark.asyncio
async def test_falha_quando_insumo_nao_esta_na_ordem():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem

    with pytest.raises(ValueError, match="não encontrado"):
        await use_case.execute(
            RemoverInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=999)
        )

    repos["insumo_repository"].find_by_id.assert_not_called()
    repos["ordem_servico_repository"].save.assert_not_called()


@pytest.mark.asyncio
async def test_nao_falha_quando_insumo_foi_excluido_do_catalogo():
    """Se o insumo foi excluído do cadastro, ainda assim remove da OS."""
    ordem = _ordem_com_insumo(quantidade=2)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = lambda o: o
    repos["insumo_repository"].find_by_id.return_value = None

    resultado = await use_case.execute(
        RemoverInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=10)
    )

    assert resultado.insumos_utilizados == []
    repos["insumo_repository"].update.assert_not_called()


@pytest.mark.asyncio
async def test_desfaz_a_transacao_quando_a_gravacao_da_os_falha():
    ordem = _ordem_com_insumo()
    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["ordem_servico_repository"].save.side_effect = RuntimeError("banco caiu")
    repos["insumo_repository"].find_by_id.return_value = Insumo(
        id=10, nome="Filtro", preco_unitario="30.00", estoque=1
    )

    with pytest.raises(RuntimeError):
        await use_case.execute(
            RemoverInsumoOrdemServicoCommand(ordem_servico_id=1, insumo_id=10)
        )

    assert repos["unit_of_work"].confirmada == 0
    assert repos["unit_of_work"].desfeita == 1
