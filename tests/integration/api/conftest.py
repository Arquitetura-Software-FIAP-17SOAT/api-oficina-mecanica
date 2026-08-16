"""App FastAPI de teste, montado com os routers reais e um banco SQLite.

Não reaproveitamos ``main.py`` porque ele chama ``create_tables()`` contra o
Postgres de produção assim que é importado. Aqui montamos uma instância nova
de ``FastAPI`` com os mesmos routers e sobrescrevemos apenas a dependência
``get_db`` para usar a sessão SQLite em memória do teste.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.database.database import get_db
from presentation.api.routes.clientes import router as clientes_router
from presentation.api.routes.insumos import router as insumos_router
from presentation.api.routes.ordens_servico import router as ordens_servico_router
from presentation.api.routes.servicos import router as servicos_router
from presentation.api.routes.users import router as users_router
from presentation.api.routes.veiculos import router as veiculos_router


@pytest.fixture()
def client(db_session) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(users_router)
    app.include_router(clientes_router)
    app.include_router(insumos_router)
    app.include_router(servicos_router)
    app.include_router(veiculos_router)
    app.include_router(ordens_servico_router)

    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client
