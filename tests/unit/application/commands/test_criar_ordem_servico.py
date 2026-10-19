import pytest
from unittest.mock import Mock, AsyncMock

from application.commands.criar_ordem_servico import (
    CriarOrdemServicoCommand,
    CriarOrdemServicoUseCase,
    VeiculoNaoEncontradoError,
)
from domain.repositories.ordem_servico_repository import OrdemServicoRepository
from tests.unit.fakes import UnitOfWorkFalso
from domain.repositories.insumo_repository import InsumoRepository
from domain.repositories.servico_repository import ServicoRepository
from domain.repositories.veiculo_repository import VeiculoRepository


class TestCriarOrdemServicoUseCase:
    """Testes para o caso de uso de criar Ordem de Serviço"""

    @pytest.mark.asyncio
    async def test_criar_ordem_servico_com_veiculo_valido(self):
        """Deve criar e persistir a ordem quando o veículo existe"""
        # Arrange
        mock_veiculo_repository = AsyncMock(spec=VeiculoRepository)
        mock_repository = AsyncMock(spec=OrdemServicoRepository)

        # Mock do veículo existente
        mock_veiculo = Mock()
        mock_veiculo.id = 1
        mock_veiculo.cliente_id = 7
        mock_veiculo_repository.find_by_id.return_value = mock_veiculo

        use_case = CriarOrdemServicoUseCase(
            ordem_servico_repository=mock_repository,
            veiculo_repository=mock_veiculo_repository,
            servico_repository=AsyncMock(spec=ServicoRepository),
            insumo_repository=AsyncMock(spec=InsumoRepository),
            unit_of_work=UnitOfWorkFalso(),
        )

        command = CriarOrdemServicoCommand(
            cliente_id=7,
            veiculo_id="1",
            descricao="Troca de óleo",
            orcamento=150.00,
            observacoes="Padrão",
        )

        # Act
        ordem_servico = await use_case.execute(command)

        # Assert
        assert ordem_servico.veiculo_id == "1"
        assert str(ordem_servico.descricao) == "Troca de óleo"
        assert ordem_servico.orcamento == 150.00
        assert ordem_servico.observacoes == "Padrão"
        mock_repository.save.assert_awaited_once_with(ordem_servico)

    def test_falhar_ao_criar_ordem_com_veiculo_inexistente(self):
        """Deve lançar exceção quando veículo não existe"""
        # Arrange
        mock_veiculo_repository = AsyncMock(spec=VeiculoRepository)
        mock_repository = AsyncMock(spec=OrdemServicoRepository)
        
        # Mock retornando nenhum veículo
        mock_veiculo_repository.find_by_id.return_value = None
        
        use_case = CriarOrdemServicoUseCase(
            ordem_servico_repository=mock_repository,
            veiculo_repository=mock_veiculo_repository,
            servico_repository=AsyncMock(spec=ServicoRepository),
            insumo_repository=AsyncMock(spec=InsumoRepository),
            unit_of_work=UnitOfWorkFalso(),
        )
        
        command = CriarOrdemServicoCommand(
            cliente_id=1,
            veiculo_id="999",  # ID inexistente
            descricao="Troca de óleo",
        )

        # Act & Assert
        with pytest.raises(VeiculoNaoEncontradoError) as exc_info:
            import asyncio
            asyncio.run(use_case.execute(command))
        
        assert "Veículo com ID 999" in str(exc_info.value)
        assert "não encontrado" in str(exc_info.value)

    def test_veiculo_nao_encontrado_error_message(self):
        """Deve ter mensagem clara de erro"""
        # Arrange
        veiculo_id = "42"
        error = VeiculoNaoEncontradoError(
            f"Veículo com ID {veiculo_id} não encontrado no banco de dados"
        )

        # Act & Assert
        assert str(error) == f"Veículo com ID {veiculo_id} não encontrado no banco de dados"
        assert isinstance(error, Exception)


@pytest.mark.asyncio
async def test_desfaz_a_transacao_quando_a_baixa_de_estoque_falha():
    """OS e baixa de estoque formam uma unidade: se uma falha, nada é confirmado."""
    from application.commands.criar_ordem_servico import InsumoSolicitado
    from domain.entities.insumo import Insumo

    veiculos = AsyncMock(spec=VeiculoRepository)
    veiculos.find_by_id.return_value = Mock(id=1, cliente_id=1)
    insumos = AsyncMock(spec=InsumoRepository)
    insumos.find_by_id.return_value = Insumo(
        id=10, nome="Filtro", preco_unitario="30.00", estoque=5
    )
    insumos.update.side_effect = RuntimeError("banco caiu")
    unit_of_work = UnitOfWorkFalso()

    use_case = CriarOrdemServicoUseCase(
        ordem_servico_repository=AsyncMock(spec=OrdemServicoRepository),
        veiculo_repository=veiculos,
        servico_repository=AsyncMock(spec=ServicoRepository),
        insumo_repository=insumos,
        unit_of_work=unit_of_work,
    )

    with pytest.raises(RuntimeError):
        await use_case.execute(
            CriarOrdemServicoCommand(
                cliente_id=1,
                veiculo_id="1",
                descricao="Troca de filtro",
                insumos=[InsumoSolicitado(insumo_id=10, quantidade=2)],
            )
        )

    assert unit_of_work.confirmada == 0
    assert unit_of_work.desfeita == 1


@pytest.mark.asyncio
async def test_falha_quando_o_veiculo_pertence_a_outro_cliente():
    veiculos = AsyncMock(spec=VeiculoRepository)
    veiculos.find_by_id.return_value = Mock(id=1, cliente_id=7)
    ordens = AsyncMock(spec=OrdemServicoRepository)

    use_case = CriarOrdemServicoUseCase(
        ordem_servico_repository=ordens,
        veiculo_repository=veiculos,
        servico_repository=AsyncMock(spec=ServicoRepository),
        insumo_repository=AsyncMock(spec=InsumoRepository),
        unit_of_work=UnitOfWorkFalso(),
    )

    with pytest.raises(ValueError, match="não pertence ao cliente"):
        await use_case.execute(
            CriarOrdemServicoCommand(cliente_id=99, veiculo_id="1", descricao="Troca de óleo")
        )

    ordens.save.assert_not_called()

