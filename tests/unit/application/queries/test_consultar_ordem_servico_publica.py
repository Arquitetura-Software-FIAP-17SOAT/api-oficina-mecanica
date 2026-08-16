from unittest.mock import AsyncMock

import pytest

from application.queries.consultar_ordem_servico_publica import (
    ConsultarOrdemServicoPublicaQuery,
    ConsultarOrdemServicoPublicaUseCase,
)
from application.queries.get_ordem_servico_detalhada import OrdemServicoDetalhada
from domain.entities.cliente import Cliente
from domain.entities.ordem_servico import OrdemServico
from domain.entities.veiculo import Veiculo


def _detalhe(cpf_cnpj: str | None = "52998224725") -> OrdemServicoDetalhada:
    ordem = OrdemServico(veiculo_id="1", descricao="Revisão completa")
    ordem.id = 1

    return OrdemServicoDetalhada(
        ordem_servico=ordem,
        veiculo=Veiculo(
            id=1, cliente_id=5, marca_id=1, placa="ABC1D23", modelo="Gol"
        ),
        cliente=Cliente(id=5, nome="Maria", usuario_id=1, cpf_cnpj=cpf_cnpj),
        itens=[],
    )


def _use_case(detalhe):
    mock_detalhada = AsyncMock()
    mock_detalhada.execute.return_value = detalhe

    return ConsultarOrdemServicoPublicaUseCase(mock_detalhada), mock_detalhada


@pytest.mark.asyncio
async def test_retorna_a_os_quando_documento_confere():
    use_case, mock_detalhada = _use_case(_detalhe())

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj="52998224725")
    )

    assert resultado is not None
    assert resultado.ordem_servico.id == 1
    mock_detalhada.execute.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_aceita_documento_com_mascara():
    """O cliente digita como está no documento dele, com pontuação."""
    use_case, _ = _use_case(_detalhe())

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj="529.982.247-25")
    )

    assert resultado is not None


@pytest.mark.asyncio
async def test_retorna_none_quando_documento_nao_confere():
    """OS de outra pessoa não pode ser consultada."""
    use_case, _ = _use_case(_detalhe(cpf_cnpj="52998224725"))

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj="11144477735")
    )

    assert resultado is None


@pytest.mark.asyncio
async def test_retorna_none_quando_os_nao_existe():
    use_case, _ = _use_case(None)

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=999, cpf_cnpj="52998224725")
    )

    assert resultado is None


@pytest.mark.asyncio
async def test_retorna_none_quando_os_nao_tem_cliente():
    """Sem cliente vinculado não há como provar titularidade."""
    detalhe = _detalhe()
    detalhe.cliente = None

    use_case, _ = _use_case(detalhe)

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj="52998224725")
    )

    assert resultado is None


@pytest.mark.asyncio
async def test_retorna_none_quando_cliente_nao_tem_documento_cadastrado():
    """Cliente sem CPF/CNPJ não pode ser autenticado por documento."""
    use_case, _ = _use_case(_detalhe(cpf_cnpj=None))

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj="52998224725")
    )

    assert resultado is None


@pytest.mark.asyncio
@pytest.mark.parametrize("documento", ["", "   ", "abc", None])
async def test_documento_vazio_nao_consulta_o_banco(documento):
    """Entrada inútil é barrada antes de chegar ao repositório."""
    use_case, mock_detalhada = _use_case(_detalhe())

    resultado = await use_case.execute(
        ConsultarOrdemServicoPublicaQuery(numero_os=1, cpf_cnpj=documento)
    )

    assert resultado is None
    mock_detalhada.execute.assert_not_called()
