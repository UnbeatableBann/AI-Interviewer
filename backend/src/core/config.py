from typing import Any, List
from pydantic import BeforeValidator, field_validator

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated


def parse_cors(v: Any) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, (list, str)):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Interviewer Intelligence Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production

    # CORS settings
    BACKEND_CORS_ORIGINS: Annotated[List[str], BeforeValidator(parse_cors)] = ["*"]

    # PostgreSQL Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "iip_db"
    DATABASE_URL: str | None = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, values: Any) -> Any:
        if isinstance(v, str) and v:
            return v

        host = values.data.get("POSTGRES_HOST", "localhost")
        port = values.data.get("POSTGRES_PORT", 5432)
        user = values.data.get("POSTGRES_USER", "postgres")
        password = values.data.get("POSTGRES_PASSWORD", "postgres")
        db = values.data.get("POSTGRES_DB", "iip_db")

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

    # Redis Config
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_URL: str | None = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: str | None, values: Any) -> Any:
        if isinstance(v, str) and v:
            return v

        host = values.data.get("REDIS_HOST", "localhost")
        port = values.data.get("REDIS_PORT", 6379)
        password = values.data.get("REDIS_PASSWORD")

        if password:
            return f"redis://:{password}@{host}:{port}/0"
        return f"redis://{host}:{port}/0"

    # Qdrant Vector DB
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str | None = None

    # MinIO Object Storage
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_NAME: str = "iip-data"

    # Security & Auth
    JWT_SECRET_KEY: str = (
        "super_secure_secret_key_change_me_in_production_9e2738ea1279ab"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
