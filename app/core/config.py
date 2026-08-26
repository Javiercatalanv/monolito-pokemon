import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Proyecto Monolito - Arquitectura de Sistemas"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"

    # CORS Origins permitidos
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            return json.loads(v)
        return v

    # Base de Datos - PostgreSQL 16 via psycopg 3.
    # Coincide con el servicio `postgres` de docker-compose.yml.
    DATABASE_URL: str = "postgresql+psycopg://pokemon:pokemon@localhost:5434/pokemon_counter"
    # Volcado de SQL a consola. Separado de DEBUG: el reload del servidor no
    # tiene por que implicar ruido de SQL en cada test.
    SQL_ECHO: bool = False

    # Servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


settings = Settings()
