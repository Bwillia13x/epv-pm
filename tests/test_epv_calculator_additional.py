import sys
from pathlib import Path
# Ensure that the 'src' directory is on the Python path for local test execution & linters
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT_DIR / "src"
if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest  # type: ignore
from datetime import date

from analysis.epv_calculator import EPVCalculator
from models.financial_models import IncomeStatement, BalanceSheet, FinancialRatios


@pytest.fixture

def sample_income_statements():
    """Provide a deterministic set of income statements spanning five years."""
    return [
        IncomeStatement("DEMO", "annual", 2023, net_income=1_000_000, revenue=10_000_000),
        IncomeStatement("DEMO", "annual", 2022, net_income=900_000, revenue=9_500_000),
        IncomeStatement("DEMO", "annual", 2021, net_income=800_000, revenue=9_000_000),
        IncomeStatement("DEMO", "annual", 2020, net_income=700_000, revenue=8_500_000),
        IncomeStatement("DEMO", "annual", 2019, net_income=650_000, revenue=8_000_000),
    ]


@pytest.fixture

def sample_balance_sheets():
    """Provide a minimal balance-sheet snapshot for leverage & liquidity tests."""
    return [
        BalanceSheet(
            "DEMO",
            "annual",
            2023,
            total_assets=5_000_000,
            current_assets=2_000_000,
            cash_and_equivalents=500_000,
            inventory=300_000,
            receivables=400_000,
            total_liabilities=2_000_000,
            current_liabilities=1_000_000,
            long_term_debt=1_000_000,
            total_equity=3_000_000,
        )
    ]


@pytest.fixture

def sample_ratios():
    today = date.today()
    return [
        FinancialRatios("DEMO", today, roe=15.0),
        FinancialRatios("DEMO", today, roe=14.0),
        FinancialRatios("DEMO", today, roe=13.0),
    ]


def test_normalized_earnings_conservative(sample_income_statements):
    """Normalized earnings should be positive and lower than the simple average due to conservatism."""
    calc = EPVCalculator()
    normalized = calc._calculate_normalized_earnings(sample_income_statements)
    avg_net_income = sum(stmt.net_income for stmt in sample_income_statements) / len(sample_income_statements)

    assert 0 < normalized < avg_net_income


@pytest.mark.parametrize(
    "net_incomes",
    [
        [1_000_000, 900_000, 800_000],  # declining slightly
        [500_000, 600_000, 700_000],    # improving earnings
    ],
)

def test_normalized_earnings_various_inputs(net_incomes):
    """Ensure the helper never returns negative values regardless of income trend."""
    calc = EPVCalculator()
    stmts = [
        IncomeStatement("VAR", "annual", 2023 - idx, net_income=net, revenue=10_000_000)
        for idx, net in enumerate(net_incomes)
    ]
    result = calc._calculate_normalized_earnings(stmts)
    assert result > 0


def test_quality_score_and_components_range(
    sample_income_statements, sample_balance_sheets, sample_ratios
):
    """Quality score must lie in [0,1] and include expected component keys."""
    calc = EPVCalculator()
    score, detailed = calc.calculate_quality_score(
        sample_income_statements, sample_balance_sheets, sample_ratios
    )

    assert 0.0 <= score <= 1.0

    expected_keys = {
        "earnings_stability",
        "roe_quality",
        "leverage_quality",
        "liquidity_quality",
        "growth_quality",
    }
    assert expected_keys.issubset(set(detailed["components"].keys()))