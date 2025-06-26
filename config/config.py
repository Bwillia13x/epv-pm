"""
Configuration settings for the EPV Research Platform
"""

from typing import Dict, Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field
from pathlib import Path


class DatabaseConfig(BaseSettings):
    """Database configuration"""

    db_url: str = Field(default="sqlite:///epv_platform.db")
    echo: bool = Field(default=False)


class DataSourceConfig(BaseSettings):
    """Data source API configuration"""

    alpha_vantage_api_key: Optional[str] = Field(
        default=None, env="ALPHA_VANTAGE_API_KEY"
    )
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")
    quandl_api_key: Optional[str] = Field(default=None, env="QUANDL_API_KEY")

    # Rate limiting
    requests_per_minute: int = Field(default=30)
    requests_per_day: int = Field(default=500)


class AnalysisConfig(BaseSettings):
    """Analysis configuration"""

    # EPV calculation parameters
    default_growth_rate: float = Field(default=0.02)  # 2% conservative growth
    risk_free_rate: float = Field(default=0.04)  # 4% risk-free rate
    market_risk_premium: float = Field(default=0.06)  # 6% market risk premium

    # Quality scoring weights
    quality_weights: Dict[str, float] = Field(
        default={
            "roe": 0.25,
            "roic": 0.25,
            "debt_to_equity": 0.15,
            "current_ratio": 0.10,
            "earnings_growth": 0.15,
            "revenue_growth": 0.10,
        }
    )

    # Lookback periods
    earnings_lookback_years: int = Field(default=10)
    revenue_lookback_years: int = Field(default=10)


class CacheConfig(BaseSettings):
    """Cache configuration"""

    cache_dir: str = Field(default="data/cache")
    cache_expiry_hours: int = Field(default=24)
    max_cache_size_mb: int = Field(default=1000)


class UIConfig(BaseSettings):
    """UI configuration"""

    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8050)
    debug: bool = Field(default=True)


class Config(BaseSettings):
    """Main configuration class"""

    project_name: str = Field(default="EPV Research Platform")
    version: str = Field(default="1.0.0")

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    data_sources: DataSourceConfig = Field(default_factory=DataSourceConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/epv_platform.log")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global configuration instance
config = Config()


# Create necessary directories
def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ["data/raw", "data/processed", "data/cache", "logs", "exports"]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    setup_directories()
    print(f"Configuration loaded for {config.project_name} v{config.version}")
