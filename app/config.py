from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Chatbot Backend"
    APP_VERSION: str = "1.1.0"
    DEPLOYMENT_ENV: str = "development"  # development | production
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # JWT auth
    ENABLE_JWT_AUTH: bool = False
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Demo auth credentials for token issuance endpoint
    DEMO_AUTH_USERNAME: str = "admin"
    DEMO_AUTH_PASSWORD: str = "password"

    # CORS
    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # Request hardening
    MAX_UPLOAD_SIZE_MB: int = 25
    MAX_INPUT_TEXT_CHARS: int = 200000

    # OpenAI dev settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4.1-nano"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # AWS production settings
    AWS_REGION: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_SESSION_TOKEN: str | None = None

    BEDROCK_MODEL_ID: str = "global.amazon.nova-2-lite-v1:0"
    BEDROCK_EMBEDDING_MODEL_ID: str = "amazon.titan-embed-text-v2:0"

    # Development vector db
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "pdf_documents"

    # Production vector db: S3 Vectors style settings
    S3_VECTORS_BUCKET: str | None = None
    S3_VECTORS_INDEX_NAME: str | None = None
    S3_VECTORS_REGION: str | None = None

    # AI defaults
    DEFAULT_MAX_TOKENS: int = 1000
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_TOP_P: float = 1.0

    # Chunking defaults
    DEFAULT_CHUNK_SIZE: int = 1200
    DEFAULT_CHUNK_OVERLAP: int = 200

    @property
    def is_production(self) -> bool:
        return self.DEPLOYMENT_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.DEPLOYMENT_ENV.lower() == "development"

    @property
    def cors_origins(self) -> list[str]:
        if self.CORS_ALLOW_ORIGINS == "*":
            return ["*"]
        return [x.strip() for x in self.CORS_ALLOW_ORIGINS.split(",") if x.strip()]

    @property
    def cors_methods(self) -> list[str]:
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [x.strip() for x in self.CORS_ALLOW_METHODS.split(",") if x.strip()]

    @property
    def cors_headers(self) -> list[str]:
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [x.strip() for x in self.CORS_ALLOW_HEADERS.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()