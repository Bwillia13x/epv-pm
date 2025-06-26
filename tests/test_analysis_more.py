from datetime import date
import pytest

from src.analysis.advanced_valuations import AdvancedValuationEngine
from src.analysis.portfolio_manager import PortfolioManager, PortfolioPosition
from src.analysis.research_generator import ResearchGenerator
from src.models.financial_models import IncomeStatement, BalanceSheet


@pytest.fixture(scope="module")
def adv_engine() -> AdvancedValuationEngine:
    return AdvancedValuationEngine()


@pytest.fixture(scope="module")
def pm() -> PortfolioManager:
    return PortfolioManager()


def _income(symbol="VAL", year=None):
    if year is None:
        year = date.today().year
    return [
        IncomeStatement(
            symbol=symbol,
            period="annual",
            fiscal_year=year,
            revenue=1_000_000,
            net_income=100_000,
            eps=1.0,
            shares_outstanding=100_000,
        )
    ]


def _balance(symbol="VAL", year=None):
    if year is None:
        year = date.today().year
    return [
        BalanceSheet(
            symbol=symbol,
            period="annual",
            fiscal_year=year,
            total_assets=2_000_000,
            total_equity=1_200_000,
            long_term_debt=100_000,
            current_assets=500_000,
            current_liabilities=250_000,
            cash_and_equivalents=200_000,
        )
    ]


def test_asset_based_valuation(adv_engine):
    inc = _income()
    bs = _balance()
    asset_val = adv_engine.calculate_asset_based_valuation("VAL", bs, inc)
    assert asset_val.book_value_per_share > 0
    assert asset_val.liquidation_value_per_share > 0


def test_market_multiples(adv_engine):
    inc = _income()
    bs = _balance()
    mm = adv_engine.calculate_market_multiples_valuation(
        symbol="VAL",
        income_statements=inc,
        balance_sheets=bs,
        current_price=20.0,
    )
    assert mm.multiples_average_value >= 0
    # PE based value should be computed
    assert mm.pe_based_value is not None


def test_rebalancing(pm):
    # current positions
    positions = [
        PortfolioPosition("AAA", 100, 10.0, 12.0, 15.0),
        PortfolioPosition("BBB", 80, 9.0, 9.5, 12.0),
    ]

    # target allocations (simple two positions 50/50)
    risk_budget = pm.create_risk_budget(max_position_size=0.6)
    allocations = pm.optimize_portfolio(
        candidates=[
            {"symbol": "AAA", "epv_per_share": 15.0, "current_price": 12.0, "quality_score": 0.7},
            {"symbol": "BBB", "epv_per_share": 12.0, "current_price": 9.5, "quality_score": 0.6},
        ],
        portfolio_value=10_000,
        risk_budget=risk_budget,
    )

    reb = pm.generate_rebalancing_recommendation(positions, allocations, rebalancing_threshold=0.01)
    assert reb is not None
    assert reb.trades_required


def test_confidence_level():
    rg = ResearchGenerator()
    conf = rg._calculate_confidence_level(quality_score=0.8, risk_score=0.2)
    assert 0.3 <= conf <= 0.95