"""Unit tests for the DataGateway and data providers.
"""
import pytest
import re
from httpx import Response, AsyncClient
from pytest_httpx import HTTPXMock
from unittest.mock import MagicMock
from typing import Optional, List, Dict, Tuple
from datetime import date

from src.data.data_gateway import DataGateway
from src.data.data_collector import DataSource, YahooFinanceSource
from src.models.financial_models import (
    IncomeStatement, BalanceSheet, CashFlowStatement, 
    MarketData, CompanyProfile, FinancialRatios
)

class MockDataSource(DataSource):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        if self.should_fail:
            raise Exception("API Error")
        return CompanyProfile(symbol=symbol, company_name="Apple Inc.")

    async def get_financial_statements(self, symbol: str, years: int = 5) -> Tuple[List, List, List]:
        if self.should_fail:
            raise Exception("API Error")
        return [IncomeStatement(symbol=symbol)], [BalanceSheet(symbol=symbol)], [CashFlowStatement(symbol=symbol)]

    async def get_market_data(self, symbol: str, start_date: date, end_date: date) -> List[MarketData]:
        if self.should_fail:
            raise Exception("API Error")
        return [MarketData(symbol=symbol, date=date.today(), price=100.0)]

    def _get_insider_transactions(self):
        pass

    async def get_quote(self, symbol: str):
        return {"symbol": symbol, "price": 100.0}

@pytest.fixture
def data_gateway(monkeypatch) -> DataGateway:
    """Returns a DataGateway instance with a mocked yfinance."""
    return DataGateway(providers=[MockDataSource(), MockDataSource(should_fail=True)])

@pytest.mark.asyncio
async def test_get_prices_success(data_gateway: DataGateway):
    """Test that get_prices returns data on success."""
    prices = await data_gateway.get_prices("AAPL")
    assert prices is not None
    assert len(prices) > 0
    assert prices[0].symbol == "AAPL"

@pytest.mark.asyncio
async def test_get_prices_fallback(data_gateway: DataGateway):
    """Test that get_prices falls back to the next provider on failure."""
    data_gateway.providers = [MockDataSource(should_fail=True), MockDataSource()]
    prices = await data_gateway.get_prices("AAPL")
    assert prices is not None
    assert len(prices) > 0
    assert prices[0].symbol == "AAPL"

@pytest.mark.asyncio
async def test_get_fundamentals_success(data_gateway: DataGateway):
    """Test that get_fundamentals returns data on success."""
    fundamentals = await data_gateway.get_fundamentals("AAPL")
    assert fundamentals is not None
    assert fundamentals["profile"] is not None

@pytest.mark.asyncio
async def test_get_fundamentals_fallback(data_gateway: DataGateway):
    """Test that get_fundamentals falls back to the next provider on failure."""
    data_gateway.providers = [MockDataSource(should_fail=True), MockDataSource()]
    fundamentals = await data_gateway.get_fundamentals("AAPL")
    assert fundamentals is not None
    assert fundamentals["profile"] is not None
