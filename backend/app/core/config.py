from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Hirify API"
    app_version: str = "2.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("CORS_ORIGINS must not be empty; required for production")
        return value

    database_url: str = f"sqlite:///{(DEFAULT_DATA_DIR / 'hirify.db').as_posix()}"
    sql_echo: bool = False

    upload_root: Path = DEFAULT_DATA_DIR / "uploads"
    resume_upload_subdir: str = "resumes"
    max_upload_bytes: int = 10 * 1024 * 1024

    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_dimensions: int = 384
    embedding_backend: str = "auto"

    match_weight_skills: float = 0.40
    match_weight_experience: float = 0.30
    match_weight_education: float = 0.20
    match_weight_additional: float = 0.10

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "production"}:
                return False
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None:
            return []

        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                return []

            # Accept JSON arrays, e.g. ["https://a.com", "https://b.com"].
            try:
                parsed = json.loads(normalized)
                if isinstance(parsed, str):
                    single = parsed.strip()
                    return [single] if single else []
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass

            # Accept comma-separated values, e.g. https://a.com,https://b.com.
            return [origin.strip() for origin in normalized.split(",") if origin.strip()]

        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]

        return value

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        if not isinstance(value, str):
            return value

        if value.startswith("postgresql+"):
            return value
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value

    @property
    def resume_upload_dir(self) -> Path:
        return self.upload_root / self.resume_upload_subdir


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_root.mkdir(parents=True, exist_ok=True)
    settings.resume_upload_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
