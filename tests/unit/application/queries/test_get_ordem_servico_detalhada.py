from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from application.queries.get_ordem_servico_detalhada import (
    GetOrdemServicoDetalhadaUseCase,
)
from domain.entities.cliente import Cliente
from domain.entities.insumo import Insumo
from domain.entities.ordem_servico import OrdemServico
from domain.entities.servico import Servico
from domain.entities.veiculo import Veiculo


def _use_case(**overrides):
    repos = dict(
        ordem_servico_repository=AsyncMock(),
        veiculo_repository=AsyncMock(),
        cliente_repository=AsyncMock(),
        servico_repository=AsyncMock(),
        insumo_repository=AsyncMock(),
    )
    repos.update(overrides)
    return GetOrdemServicoDetalhadaUseCase(**repos), repos


@pytest.mark.asyncio
async def test_retorna_none_quando_ordem_nao_existe():
    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = None

    resultado = await use_case.execute(999)

    assert resultado is None
    repos["veiculo_repository"].find_by_id.assert_not_called()


@pytest.mark.asyncio
async def test_monta_detalhe_completo_com_cliente_veiculo_e_itens():
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1
    ordem.adicionar_item("10", 150.0, quantidade=2)

    veiculo = Veiculo(id=1, cliente_id=5, marca_id=1, placa="ABC1D23", modelo="Gol")
    cliente = Cliente(id=5, nome="Maria", usuario_id=1)
    servico = Servico(id=10, nome="Troca de óleo", valor=Decimal("150.00"))
    insumo = Insumo(id=20, nome="Óleo 5W30", estoque=10)

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["veiculo_repository"].find_by_id.return_value = veiculo
    repos["cliente_repository"].find_by_id.return_value = cliente
    repos["servico_repository"].find_by_id.return_value = servico
    repos["insumo_repository"].list_by_servico_id.return_value = [insumo]

    detalhe = await use_case.execute(1)

    repos["veiculo_repository"].find_by_id.assert_awaited_once_with(1)
    repos["cliente_repository"].find_by_id.assert_awaited_once_with(5)
    repos["servico_repository"].find_by_id.assert_awaited_once_with(10)
    repos["insumo_repository"].list_by_servico_id.assert_awaited_once_with(10)

    assert detalhe.cliente is cliente
    assert detalhe.veiculo is veiculo
    assert len(detalhe.itens) == 1

    item = detalhe.itens[0]
    assert item.servico is servico
    assert item.quantidade == 2
    assert item.valor_unitario == 150.0
    assert item.valor_total == 300.0
    assert item.insumos == [insumo]
    assert detalhe.valor_total_itens == 300.0


@pytest.mark.asyncio
async def test_detalhe_sem_veiculo_nao_busca_cliente():
    ordem = OrdemServico(veiculo_id="999", descricao="Revisão completa")
    ordem.id = 1

    use_case, repos = _use_case()
    repos["ordem_servico_repository"].find_by_id.return_value = ordem
    repos["veiculo_repository"].find_by_id.return_value = None

    detalhe = await use_case.execute(1)

    assert detalhe.veiculo is None
    assert detalhe.cliente is None
    repos["cliente_repository"].find_by_id.assert_not_called()
