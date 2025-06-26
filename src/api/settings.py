"""
API settings and configuration using pydantic-settings
"""
try:
    from pydantic_settings import BaseSettings  # type: ignore
except ImportError:  # Fallback for environments without pydantic-settings
    from pydantic import BaseSettings  # type: ignore

class Settings(BaseSettings):
    # API keys
    alpha_vantage_api_key: str = "demo"
    fred_api_key: str = "demo"
    quandl_api_key: str = "demo"

    # Application settings
    app_name: str = "EPV Research Platform API"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
