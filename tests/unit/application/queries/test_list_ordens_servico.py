from unittest.mock import AsyncMock

import pytest

from application.queries.list_ordens_servico import (
    ListOrdensServicoQuery,
    ListOrdensServicoUseCase,
    OrdensServicoPaginadas,
)


@pytest.mark.asyncio
async def test_lista_com_paginacao_padrao():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 0)

    use_case = ListOrdensServicoUseCase(mock_repository)
    resultado = await use_case.execute(ListOrdensServicoQuery())

    mock_repository.list_paginado.assert_awaited_once_with(
        skip=0, limit=10, status=None, cpf_cnpj=None, placa=None
    )
    assert resultado.page == 1
    assert resultado.page_size == 10


@pytest.mark.asyncio
async def test_calcula_skip_a_partir_da_pagina():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 25)

    use_case = ListOrdensServicoUseCase(mock_repository)
    resultado = await use_case.execute(
        ListOrdensServicoQuery(page=3, page_size=10)
    )

    mock_repository.list_paginado.assert_awaited_once_with(
        skip=20, limit=10, status=None, cpf_cnpj=None, placa=None
    )
    assert resultado.total_paginas == 3


@pytest.mark.asyncio
async def test_pagina_minima_e_um():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 0)

    use_case = ListOrdensServicoUseCase(mock_repository)
    await use_case.execute(ListOrdensServicoQuery(page=0, page_size=0))

    mock_repository.list_paginado.assert_awaited_once_with(
        skip=0, limit=1, status=None, cpf_cnpj=None, placa=None
    )


@pytest.mark.asyncio
async def test_page_size_e_limitado_ao_maximo():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 0)

    use_case = ListOrdensServicoUseCase(mock_repository)
    await use_case.execute(ListOrdensServicoQuery(page_size=1000))

    _, kwargs = mock_repository.list_paginado.await_args
    assert kwargs["limit"] == ListOrdensServicoUseCase.PAGE_SIZE_MAXIMO


@pytest.mark.asyncio
async def test_normaliza_cpf_cnpj_e_placa_com_mascara():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 0)

    use_case = ListOrdensServicoUseCase(mock_repository)
    await use_case.execute(
        ListOrdensServicoQuery(cpf_cnpj="529.982.247-25", placa="abc-1d23")
    )

    mock_repository.list_paginado.assert_awaited_once_with(
        skip=0, limit=10, status=None, cpf_cnpj="52998224725", placa="ABC1D23"
    )


@pytest.mark.asyncio
async def test_falha_com_status_invalido():
    mock_repository = AsyncMock()

    use_case = ListOrdensServicoUseCase(mock_repository)

    with pytest.raises(ValueError, match="Status inválido"):
        await use_case.execute(ListOrdensServicoQuery(status="Inexistente"))

    mock_repository.list_paginado.assert_not_called()


@pytest.mark.asyncio
async def test_aceita_status_valido():
    mock_repository = AsyncMock()
    mock_repository.list_paginado.return_value = ([], 1)

    use_case = ListOrdensServicoUseCase(mock_repository)
    await use_case.execute(ListOrdensServicoQuery(status="Recebida"))

    mock_repository.list_paginado.assert_awaited_once_with(
        skip=0, limit=10, status="Recebida", cpf_cnpj=None, placa=None
    )


def test_total_paginas_com_page_size_zero():
    paginadas = OrdensServicoPaginadas(itens=[], total=10, page=1, page_size=0)

    assert paginadas.total_paginas == 0
