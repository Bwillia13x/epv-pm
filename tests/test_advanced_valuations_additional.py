import sys
from pathlib import Path
import numpy as np  # type: ignore
import pytest  # type: ignore
from datetime import date

# Add src to path for local execution
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT_DIR / "src"
if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.advanced_valuations import AdvancedValuationEngine
from models.financial_models import IncomeStatement, BalanceSheet, CashFlowStatement


@pytest.fixture

def engine():
    # Ensure deterministic behaviour for any NumPy randomness inside the module
    np.random.seed(0)
    return AdvancedValuationEngine()


@pytest.fixture

def sample_income():
    return [
        IncomeStatement("SAMP", "annual", 2020, revenue=10_000_000, net_income=800_000),
        IncomeStatement("SAMP", "annual", 2021, revenue=10_500_000, net_income=900_000),
        IncomeStatement("SAMP", "annual", 2022, revenue=11_000_000, net_income=1_000_000),
    ]


def test_project_revenues_length(engine, sample_income):
    years = 4
    projections = engine._project_revenues(sample_income, years)
    # Correct length
    assert len(projections) == years
    # First projected revenue should exceed the last historical revenue due to positive growth
    assert projections[0] > sample_income[-1].revenue


def test_project_free_cash_flows_non_negative(engine, sample_income):
    revenue_proj = engine._project_revenues(sample_income, 3)
    cashflows = [
        CashFlowStatement("SAMP", "annual", 2022, operating_cash_flow=1_200_000, free_cash_flow=750_000)
    ]
    fcf = engine._project_free_cash_flows(sample_income, cashflows, revenue_proj)
    assert len(fcf) == 3
    assert all(val >= 0 for val in fcf)


@pytest.mark.parametrize(
    "assets,debt,expected_relation",[
        (5e8, 1e8, "high"),  # small company -> higher discount rate
        (20e9, 1e9, "low"),  # large company -> lower discount rate
    ])

def test_estimate_discount_rate_relative(engine, assets, debt, expected_relation):
    bs = [BalanceSheet("TEST", "annual", 2023, total_assets=assets, total_equity=assets/2, long_term_debt=debt)]
    inc = [IncomeStatement("TEST", "annual", 2023, net_income=1_000_000)]
    rate = engine._estimate_discount_rate(bs, inc)
    # Always at least 8%
    assert rate >= 0.08
    if expected_relation == "high":
        # Comparing to a benchmark large co discount rate
        bs_large = [BalanceSheet("L", "annual", 2023, total_assets=20e9, total_equity=10e9, long_term_debt=1e9)]
        large_rate = engine._estimate_discount_rate(bs_large, inc)
        assert rate >= large_rate
    else:
        bs_small = [BalanceSheet("S", "annual", 2023, total_assets=5e8, total_equity=3e8, long_term_debt=1e8)]
        small_rate = engine._estimate_discount_rate(bs_small, inc)
        assert rate <= small_rate