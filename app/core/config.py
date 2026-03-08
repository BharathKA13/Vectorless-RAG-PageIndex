"""
Centralised application settings.

All secrets and tunables are loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── PageIndex ──
    PAGEINDEX_API_KEY: str = Field(..., description="API key from https://dash.pageindex.ai/api-keys")

    # ── OpenAI ──
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4.1", description="Chat model to use")
    OPENAI_TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0)

    # ── App ──
    UPLOAD_DIR: str = Field(default="data", description="Directory to persist uploaded PDFs")
    POLL_INTERVAL: int = Field(default=5, ge=1, description="Seconds between PageIndex ready checks")
    MAX_WAIT_SECONDS: int = Field(default=300, ge=10, description="Maximum seconds to wait for PageIndex processing")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()