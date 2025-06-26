"""
Unit tests for the DataGateway and data providers.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.data.data_gateway import DataGateway
from src.data.data_collector import YahooFinanceSource, AlphaVantageSource, FredSource
from src.models.financial_models import MarketData

@pytest.fixture
def mock_yahoo_source(monkeypatch):
    mock = MagicMock(spec=YahooFinanceSource)
    mock.get_quote = AsyncMock(return_value={"symbol": "AAPL", "price": 150.0, "provider": "YahooFinance"})
    return mock

@pytest.fixture
def mock_alpha_vantage_source(monkeypatch):
    mock = MagicMock(spec=AlphaVantageSource)
    mock.get_quote = AsyncMock(return_value={"symbol": "AAPL", "price": 151.0, "provider": "AlphaVantage"})
    return mock

@pytest.fixture
def mock_fred_source(monkeypatch):
    mock = MagicMock(spec=FredSource)
    mock.get_quote = AsyncMock(return_value=None)
    return mock

@pytest.mark.asyncio
async def test_get_quote_success_primary(mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source):
    """Test that get_quote returns data from the primary provider on success."""
    gateway = DataGateway(providers=[mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source])
    quote = await gateway.get_quote("AAPL")
    assert quote is not None
    assert quote["provider"] == "YahooFinance"

@pytest.mark.asyncio
async def test_get_quote_fallback(mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source):
    """Test that get_quote falls back to the next provider on failure."""
    mock_yahoo_source.get_quote.side_effect = Exception("API Error")
    gateway = DataGateway(providers=[mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source])
    quote = await gateway.get_quote("AAPL")
    assert quote is not None
    assert quote["provider"] == "AlphaVantage"

@pytest.mark.asyncio
async def test_get_quote_all_fail(mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source):
    """Test that get_quote returns None when all providers fail."""
    mock_yahoo_source.get_quote.side_effect = Exception("API Error")
    mock_alpha_vantage_source.get_quote.side_effect = Exception("API Error")
    gateway = DataGateway(providers=[mock_yahoo_source, mock_alpha_vantage_source, mock_fred_source])
    quote = await gateway.get_quote("AAPL")
    assert quote is None
