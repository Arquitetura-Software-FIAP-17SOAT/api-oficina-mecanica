import pytest
from pydantic import ValidationError

from adapters.config.config import Settings


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch):
    for nome in (
        "JWT_SECRET_KEY",
        "JWT_ALGORITHM",
        "JWT_EXPIRE_MINUTES",
        "INTEGRACAO_API_KEY",
        "SECRET_KEY",
    ):
        monkeypatch.delenv(nome, raising=False)


def _settings() -> Settings:
    return Settings(_env_file=None)


def test_a_aplicacao_nao_sobe_sem_o_segredo_jwt():
    with pytest.raises(ValidationError):
        _settings()


def test_le_as_variaveis_jwt_do_ambiente(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "meu-segredo")
    monkeypatch.setenv("JWT_ALGORITHM", "HS512")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "15")

    config = _settings()

    assert config.SECRET_KEY == "meu-segredo"
    assert config.ALGORITHM == "HS512"
    assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 15


def test_valores_padrao_de_algoritmo_e_expiracao(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "meu-segredo")

    config = _settings()

    assert config.ALGORITHM == "HS256"
    assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 60


def test_nome_antigo_da_variavel_nao_define_o_segredo(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "nome-antigo")

    with pytest.raises(ValidationError):
        _settings()


def test_chave_de_integracao_e_opcional(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "meu-segredo")

    assert _settings().INTEGRACAO_API_KEY is None

    monkeypatch.setenv("INTEGRACAO_API_KEY", "chave")
    assert _settings().INTEGRACAO_API_KEY == "chave"
