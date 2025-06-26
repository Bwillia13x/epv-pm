"""
API settings and configuration using pydantic-settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # API keys
    alpha_vantage_api_key: str = "demo"
    fred_api_key: str = "demo"
    quandl_api_key: str = "demo"

    # Application settings
    app_name: str = "EPV Research Platform API"
    log_level: str = "INFO"

    # Feature flags
    pdf_enabled: bool = Field(False, env="PDF_ENABLED")

    class Config:
        env_file = ".env"


settings = Settings()
