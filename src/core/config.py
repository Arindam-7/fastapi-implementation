from typing import Literal, Any
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Instruct Pydantic to read from a local .env file securely
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )
    
    PROJECT_NAME: str = "FASTAPI best practices"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment targeting
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    
    # Database Environment Signatures
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: PostgresDsn | None = None

    # Redis & Celery Environment Signatures
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str | None = None

    # Cryptographic JWT Specifications
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    def model_post_init(self, __context: Any) -> None:
        """Construct database and worker connection DSNs post parsing."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn(
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                f"{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
            )
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

# Instantiating this object triggers environment variable parsing and validation
settings = Settings()
