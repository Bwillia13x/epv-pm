import sys
from pathlib import Path
from datetime import date
import pytest  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.research_generator import ResearchGenerator  # type: ignore
from models.financial_models import (  # type: ignore
    CompanyProfile,
    EPVCalculation,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
)


@pytest.fixture
def rg():
    return ResearchGenerator()


def _minimal_epv(mos: float = 0) -> EPVCalculation:
    return EPVCalculation(
        symbol="XYZ",
        calculation_date=date.today(),
        normalized_earnings=1_000_000,
        shares_outstanding=100_000,
        cost_of_capital=0.1,
        earnings_per_share=10.0,
        epv_per_share=100.0,
        epv_total=10_000_000,
        margin_of_safety=mos,
        quality_score=0.6,
    )


def _fake_company_data(symbol: str = "XYZ") -> dict:
    profile = CompanyProfile(symbol=symbol, company_name=f"{symbol} Corp")
    income = [IncomeStatement(symbol, "annual", 2023, net_income=1_000_000, revenue=5_000_000)]
    bal = [BalanceSheet(symbol, "annual", 2023, total_equity=2_000_000)]
    cf = [CashFlowStatement(symbol, "annual", 2023, operating_cash_flow=800_000, free_cash_flow=600_000)]
    ratios = [FinancialRatios(symbol, date.today(), roe=15.0)]
    return {
        "profile": profile,
        "income_statements": income,
        "balance_sheets": bal,
        "cash_flow_statements": cf,
        "financial_ratios": ratios,
    }


@pytest.mark.parametrize(
    "mos,quality_expected",
    [
        (25, "undervalued"),
        (-10, "overvalued"),
    ],
)

def test_generate_investment_thesis_contains_mos(rg, mos, quality_expected):
    thesis = rg._generate_investment_thesis(
        _fake_company_data(), _minimal_epv(mos),
        {"overall_score":0.6, "components":{}, "interpretation":"Good"},
        {},
    )
    assert quality_expected in thesis.lower()


def test_summarize_peer_comparison_ranges(rg):
    peers = {
        "AAA": {"epv_per_share": 120, "quality_score": 0.8},
        "BBB": {"epv_per_share": 80, "quality_score": 0.5},
        "CCC": {"epv_per_share": 100, "quality_score": 0.6},
    }
    summary = rg._summarize_peer_comparison("XYZ", peers)
    assert summary["peer_count"] == 3
    assert summary["peer_epv_range"] == (80,120)
    assert summary["peer_quality_range"] == (0.5,0.8)