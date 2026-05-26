"""Centralized application settings loaded from environment variables."""

# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """All application configuration — sourced from .env or environment."""

    # LLM
    openai_api_key: str = Field(default="", description="OpenAI API key")
    google_api_key: str = Field(default="", description="Google AI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    llm_provider: str = Field(default="openai", description="LLM provider: openai | gemini | claude | custom")
    
    # Custom / OpenAI-compatible endpoint (Groq, OpenRouter, etc.)
    custom_llm_api_key: str = Field(default="", description="Custom provider API key")
    custom_llm_base_url: str = Field(default="", description="Custom provider base URL")
    custom_llm_model: str = Field(default="", description="Custom provider model name")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./dev.db",
        description="Primary database connection string",
    )
    sqlite_fallback_path: str = Field(default="./dev.db", description="SQLite fallback path")

    # Agent tuning
    max_retries: int = Field(default=3, ge=1, le=10, description="Max SQL self-correction retries")
    schema_cache_ttl: int = Field(default=300, ge=0, description="Schema cache TTL in seconds")
    max_result_rows: int = Field(default=100, ge=1, description="Max rows returned to client")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }

    @property
    def db_dialect(self) -> str:
        """Extract SQL dialect from the connection URL for prompt injection."""
        if "postgresql" in self.database_url:
            return "PostgreSQL"
        elif "sqlite" in self.database_url:
            return "SQLite"
        return "SQL"


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings instance — cached for the process lifetime."""
    return Settings()
