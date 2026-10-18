from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "42B38697D6C921058DDCFDD5ED5D89FAF0C671E3"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Chave dos sistemas externos que notificam a oficina; sem ela a integração fica desligada.
    INTEGRACAO_API_KEY: str | None = None

settings = Settings()