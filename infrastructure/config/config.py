from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "42B38697D6C921058DDCFDD5ED5D89FAF0C671E3"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()