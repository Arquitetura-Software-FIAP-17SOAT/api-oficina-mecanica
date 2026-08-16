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


def _montar_app(db_session) -> FastAPI:
    app = FastAPI()
    app.include_router(users_router)
    app.include_router(clientes_router)
    app.include_router(insumos_router)
    app.include_router(servicos_router)
    app.include_router(veiculos_router)
    app.include_router(ordens_servico_router)

    app.dependency_overrides[get_db] = lambda: db_session

    return app


def _autenticar(test_client: TestClient) -> str:
    """Registra e autentica um usuário administrativo, devolvendo o token."""

    test_client.post(
        "/users/register",
        json={
            "name": "Usuário Admin",
            "email": "admin@example.com",
            "password": "senha-super-secreta",
        },
    )

    resposta = test_client.post(
        "/users/login",
        json={"email": "admin@example.com", "password": "senha-super-secreta"},
    )

    return resposta.json()["access_token"]


@pytest.fixture()
def unauthenticated_client(db_session) -> Iterator[TestClient]:
    """Client sem token — para testar o comportamento das rotas sem autenticação.

    É uma instância independente de ``client`` (app própria), mas aponta para o
    mesmo ``db_session``, então enxerga os mesmos dados criados pelo client
    autenticado no mesmo teste.
    """

    with TestClient(_montar_app(db_session)) as test_client:
        yield test_client


@pytest.fixture()
def client(db_session) -> Iterator[TestClient]:
    """Client autenticado como usuário administrativo por padrão.

    Todas as rotas administrativas agora exigem JWT (``Depends(get_current_user)``
    no nível do ``APIRouter``), então a maioria dos testes de integração quer um
    client já autenticado. Os poucos testes que verificam o comportamento sem
    token usam ``unauthenticated_client``.
    """

    with TestClient(_montar_app(db_session)) as test_client:
        token = _autenticar(test_client)
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    """Header Authorization equivalente ao já aplicado por padrão em ``client``."""

    return {"Authorization": client.headers["Authorization"]}
