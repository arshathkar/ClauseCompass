from pathlib import Path
from typing import List, Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve project root: backend/app/core/settings.py → backend/app/core → backend/app → backend → project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    llm_mode: Literal["live", "replay", "fake"] = "replay"

    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_api_key: Optional[str] = None
    llm_model_fast: str = "gemini-3.5-flash-lite"
    llm_model_analysis: str = "gemini-3.5-flash-lite"

    llm_secondary_models: str = ""

    llm_fallback_base_url: str = "https://api.groq.com/openai/v1"
    llm_fallback_api_key: Optional[str] = None
    llm_fallback_model: str = "openai/gpt-oss-120b"

    llm_rpm_limit: int = 12
    llm_concurrency: int = 3
    llm_timeout_analysis_s: int = 45
    llm_timeout_fast_s: int = 15
    llm_max_retries: int = 3

    calls_per_analysis_max: int = 8
    calls_per_session_max: int = 30
    tokens_per_session_max: int = 300000

    session_ttl_min: int = 60
    max_text_chars: int = 400000

    allowed_origins: str = "http://localhost:5173"
    free_tier_notice: bool = True

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def project_root(self) -> Path:
        return _PROJECT_ROOT

    @property
    def data_dir(self) -> Path:
        return _PROJECT_ROOT / "data"

    @property
    def secondary_models_list(self) -> List[str]:
        if not self.llm_secondary_models:
            return []
        return [m.strip() for m in self.llm_secondary_models.split(",")]

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
