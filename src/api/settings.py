"""
API settings and configuration using pydantic-settings
"""
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API keys loaded from environment variables (no insecure defaults)
    alpha_vantage_api_key: Optional[str] = Field(default=None, env="ALPHA_VANTAGE_API_KEY")
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")
    quandl_api_key: Optional[str] = Field(default=None, env="QUANDL_API_KEY")

    # Application settings
    app_name: str = "EPV Research Platform API"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
