"""
Data gateway for fetching financial data from multiple providers
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

from .data_collector import DataSource, YahooFinanceSource, AlphaVantageSource, FredSource
from utils.cache_manager import CacheManager
from api.settings import settings

class DataGateway:
    """
    A gateway for fetching financial data from multiple providers with a fallback and caching strategy.
    """

    def __init__(self, cache_manager: Optional[CacheManager] = None, providers: Optional[List[DataSource]] = None):
        self.logger = logging.getLogger(__name__)
        self.cache_manager = cache_manager or CacheManager()
        self.providers: List[DataSource] = providers or [
            YahooFinanceSource(),
            AlphaVantageSource(api_key=settings.alpha_vantage_api_key),
            FredSource(api_key=settings.fred_api_key),
        ]
        self.quote_cache = {} # In-memory cache for quotes

    async def get_prices(self, symbol: str) -> Optional[List[Dict]]:
        """Get historical prices for a symbol."""
        cache_key = f"prices_{symbol}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            self.logger.info(f"Using cached price data for {symbol}")
            return cached_data

        for provider in self.providers:
            try:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=365 * 5)  # 5 years of data
                prices = await provider.get_market_data(symbol, start_date, end_date)
                if prices:
                    self.logger.info(f"Fetched price data for {symbol} from {provider.__class__.__name__}")
                    self.cache_manager.set(cache_key, prices)
                    return prices
            except Exception as e:
                self.logger.warning(f"Failed to fetch price data for {symbol} from {provider.__class__.__name__}: {e}")

        self.logger.error(f"Failed to fetch price data for {symbol} from all providers.")
        return None

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get the latest quote for a symbol."""
        if symbol in self.quote_cache:
            self.logger.info(f"Using in-memory quote for {symbol}")
            return self.quote_cache[symbol]

        for provider in self.providers:
            try:
                quote = await provider.get_quote(symbol)
                if quote:
                    self.logger.info(f"Fetched quote for {symbol} from {provider.__class__.__name__}")
                    self.quote_cache[symbol] = quote
                    return quote
            except Exception as e:
                self.logger.warning(f"Failed to fetch quote for {symbol} from {provider.__class__.__name__}: {e}")

        self.logger.error(f"Failed to fetch quote for {symbol} from all providers.")
        return None

    async def get_fundamentals(self, symbol: str) -> Optional[Dict]:
        """Get fundamental data for a symbol."""
        cache_key = f"fundamentals_{symbol}"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            self.logger.info(f"Using cached fundamental data for {symbol}")
            return cached_data

        for provider in self.providers:
            try:
                profile = await provider.get_company_profile(symbol)
                income, balance, cashflow = await provider.get_financial_statements(symbol)
                if profile and income and balance and cashflow:
                    fundamentals = {
                        "profile": profile,
                        "income_statement": income,
                        "balance_sheet": balance,
                        "cash_flow_statement": cashflow,
                    }
                    self.logger.info(f"Fetched fundamental data for {symbol} from {provider.__class__.__name__}")
                    self.cache_manager.set(cache_key, fundamentals)
                    return fundamentals
            except Exception as e:
                self.logger.warning(f"Failed to fetch fundamental data for {symbol} from {provider.__class__.__name__}: {e}")
        
        self.logger.error(f"Failed to fetch fundamental data for {symbol} from all providers.")
        return None
