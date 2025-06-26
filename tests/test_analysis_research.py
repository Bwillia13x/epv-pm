from datetime import date
from types import SimpleNamespace

import pytest

from src.analysis.research_generator import ResearchGenerator
from src.models.financial_models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
    MarketData,
    CompanyProfile,
)


class DummyCollector:
    """Stub for DataCollector returning deterministic data."""

    def __init__(self):
        self.called = False

    def collect_company_data(self, symbol: str, years: int):  # noqa: D401
        self.called = True
        current_year = date.today().year
        income = [
            IncomeStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=current_year - i,
                net_income=1_000_000 + i * 100_000,
                revenue=10_000_000 + i * 1_000_000,
                shares_outstanding=1_000_000,
            )
            for i in range(3)
        ]
        balance = [
            BalanceSheet(
                symbol=symbol,
                period="annual",
                fiscal_year=current_year - i,
                total_assets=5_000_000,
                total_equity=3_000_000,
                long_term_debt=500_000,
                current_assets=2_000_000,
                current_liabilities=1_000_000,
            )
            for i in range(3)
        ]
        cash_flows = [
            CashFlowStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=current_year - i,
                operating_cash_flow=1_200_000,
                free_cash_flow=800_000,
                capital_expenditures=-400_000,
            )
            for i in range(3)
        ]
        ratios = [
            FinancialRatios(symbol=symbol, calculation_date=date.today(), roe=12.0)
        ]
        market_data = [
            MarketData(symbol=symbol, date=date.today(), price=25.0)
        ]
        return {
            "symbol": symbol,
            "profile": CompanyProfile(symbol=symbol, company_name="Dummy Corp"),
            "income_statements": income,
            "balance_sheets": balance,
            "cash_flow_statements": cash_flows,
            "financial_ratios": ratios,
            "market_data": market_data,
        }

    def get_peer_comparison_data(self, symbol: str, peers):  # noqa: D401
        return {"target": symbol, "peers": {}}


@pytest.fixture(scope="module")
def generator() -> ResearchGenerator:
    gen = ResearchGenerator()
    # type: ignore - runtime patch for testing
    dummy = DummyCollector()
    setattr(gen, "data_collector", dummy)  # noqa: B010
    return gen


def test_generate_research_report(generator: ResearchGenerator):
    report = generator.generate_research_report(symbol="DUM")
    assert report.symbol == "DUM"
    assert report.epv_calculation is not None
    assert report.quality_score is not None
    # ensure dummy collector was used
    assert getattr(generator.data_collector, "called", False)