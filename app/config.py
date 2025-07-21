import os
from pydantic import Field, model_validator
from typing import Optional
from pydantic_settings import BaseSettings
from sqlalchemy.engine.url import make_url, URL

DEFAULT_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/quore"
DEFAULT_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/quore_test"


class Settings(BaseSettings):
    app_name: str = "Quore"
    vaulta_api_url: str = Field(
        default="http://localhost:8004", json_schema_extra={"env": "VAULTA_API_URL"}
    )
    otel_enabled: bool = Field(default=False, json_schema_extra={"env": "OTEL_ENABLED"})
    database_url: Optional[str] = None  # Will be set dynamically
    environment: str = Field(default="development", json_schema_extra={"env": "ENV"})
    log_level: str = Field(default="INFO", json_schema_extra={"env": "LOG_LEVEL"})
    disable_auth: bool = Field(default=False, json_schema_extra={"env": "DISABLE_AUTH"})
    port: int = Field(default=8000, json_schema_extra={"env": "PORT"})
    identies_host: Optional[str] = Field(
        default=None,
        json_schema_extra={"env": "IDENTIES_HOST"},
    )
    rollbar_access_token: Optional[str] = Field(
        default=None, json_schema_extra={"env": "ROLLBAR_ACCESS_TOKEN"}
    )  # Optional field

    credential_master_key: Optional[str] = Field(
        default=None, json_schema_extra={"env": "CREDENTIAL_MASTER_KEY"}
    )  # Optional field
    oidc_domain: str = "test.oidc.com"
    oidc_api_audience: str = "https://test-api"
    oidc_issuer: str = "https://test.oidc.com/"
    oidc_algorithms: str = "RS256"
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "quore"
    default_data_dir: str = "data"
    default_llm_provider: str = "openai"
    default_llm: str = "gpt-4o"
    default_embed_model: str = "text-embedding-3-small"
    default_embed_dim: int = 1536
    default_hnsw_m: int = 16
    default_hnsw_ef_construction: int = 64
    default_hnsw_ef_search: int = 40
    default_hnsw_dist_method: str = "vector_cosine_ops"
    default_system_prompt: str = "You are a helpful assistant."
    openai_api_key: str = Field(default="", json_schema_extra={"env": "ENV"})
    redis_host: str = Field(
        default="localhost", json_schema_extra={"env": "REDIS_HOST"}
    )
    redis_port: int = Field(default=6379, json_schema_extra={"env": "REDIS_PORT"})
    redis_namespace: str = Field(
        default="llama_index", json_schema_extra={"env": "REDIS_NAMESPACE"}
    )

    @model_validator(mode="before")
    def set_database_url(cls, values):
        """Set the database_url dynamically based on the environment field."""
        environment = values.get("environment", os.getenv("ENV", "development"))
        if environment.lower() == "test":
            values["database_url"] = os.getenv(
                "TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL
            )
        else:
            values["database_url"] = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

        return values

    @property
    def is_production(self) -> bool:
        """Check if the current environment is production."""
        return self.environment.lower() == "production"

    @property
    def is_test(self) -> bool:
        """Check if the current environment is test."""
        return self.environment.lower() == "test"

    @property
    def database_url_obj(self) -> URL:
        """Return the database URL as a URL object using sqlalchemy's make_url."""
        if not self.database_url:
            raise ValueError("Database URL is not set.")
        return make_url(self.database_url)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra environment variables


def get_settings() -> Settings:
    """Get application settings with required environment variables."""
    return Settings()
