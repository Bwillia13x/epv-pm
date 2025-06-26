"""Unit tests for the DataGateway and data providers."""

import pytest
from typing import Optional, List, Dict, Tuple
from datetime import date

from src.data.data_gateway import DataGateway
from src.data.data_collector import DataSource
from src.models.financial_models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketData,
    CompanyProfile,
)


class MockDataSource(DataSource):
    def __init__(self, should_fail=False):
        self.should_fail = should_fail

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        if self.should_fail:
            raise Exception("API Error")
        return CompanyProfile(symbol=symbol, company_name="Apple Inc.")

    async def get_financial_statements(
        self, symbol: str, years: int = 5
    ) -> Tuple[List, List, List]:
        if self.should_fail:
            raise Exception("API Error")
        dummy_kwargs = {"symbol": symbol, "period": "annual", "fiscal_year": 2025}
        income = IncomeStatement(**dummy_kwargs)
        balance = BalanceSheet(**dummy_kwargs)
        cash = CashFlowStatement(**dummy_kwargs)
        return [income], [balance], [cash]

    async def get_market_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[MarketData]:
        if self.should_fail:
            raise Exception("API Error")
        return [MarketData(symbol=symbol, date=date.today(), price=100.0)]

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Return a mocked real-time quote."""
        if self.should_fail:
            raise Exception("API Error")
        return {
            "symbol": symbol,
            "price": 100.0,
            "timestamp": "2025-01-01T00:00:00Z",
            "provider": "Mock",
        }


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
