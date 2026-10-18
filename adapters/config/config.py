from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração lida do ambiente (e do arquivo ``.env``, se existir)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Obrigatória e sem valor padrão: sem ``JWT_SECRET_KEY`` a aplicação não sobe,
    # em vez de assinar tokens com um segredo conhecido.
    SECRET_KEY: str = Field(validation_alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field("HS256", validation_alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, validation_alias="JWT_EXPIRE_MINUTES")
    # Chave dos sistemas externos que notificam a oficina; sem ela a integração fica desligada.
    INTEGRACAO_API_KEY: str | None = None


settings = Settings()
