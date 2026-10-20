from fastapi.testclient import TestClient


def test_importar_o_main_nao_cria_tabelas(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        "adapters.database.database.create_tables", lambda: chamadas.append(1)
    )

    import importlib

    import main

    importlib.reload(main)

    assert chamadas == []


def test_tabelas_sao_criadas_na_subida_da_aplicacao(monkeypatch):
    import main

    chamadas = []
    monkeypatch.setattr(main, "create_tables", lambda: chamadas.append(1))

    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "UP"}

    assert chamadas == [1]
