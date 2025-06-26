import sys
from pathlib import Path
import numpy as np
import pytest  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.advanced_valuations import AdvancedValuationEngine  # type: ignore
from models.financial_models import IncomeStatement, CashFlowStatement, BalanceSheet  # type: ignore


@pytest.fixture
def engine():
    np.random.seed(42)
    return AdvancedValuationEngine()

# ------------------ _project_revenues ---------------------------------------
@pytest.mark.parametrize("revenues,years", [
    ([10_000, 11_000, 12_000], 4),
    ([5_000, 5_500, 6_500, 7_000], 3),
])

def test_project_revenues_monotonic(engine, revenues, years):
    stmts = [
        IncomeStatement("AAA", "annual", 2020 + idx, revenue=r) for idx, r in enumerate(revenues)
    ]
    proj = engine._project_revenues(stmts, years)
    # Correct length & no negative values
    assert len(proj) == years
    assert all(p > 0 for p in proj)
    # First projection should be >= last historical revenue (growth assumption)
    assert proj[0] >= revenues[-1]

# ------------------ _estimate_discount_rate ----------------------------------
@pytest.mark.parametrize("assets,debt,expected_min", [
    (0.5e9, 0.1e9, 0.09),  # small cap -> higher rate
    (20e9, 1e9, 0.08),     # large cap minimal bound 8%
])

def test_estimate_discount_rate_bounds(engine, assets, debt, expected_min):
    bs = [BalanceSheet("BBB", "annual", 2023, total_assets=assets, total_equity=assets/2, long_term_debt=debt)]
    inc = [IncomeStatement("BBB", "annual", 2023, net_income=1_000_000)]
    rate = engine._estimate_discount_rate(bs, inc)
    assert rate >= expected_min
    # never below hard minimum 8%
    assert rate >= 0.08

# -------------- _project_free_cash_flows -------------------------------------

def test_project_fcf_positive(engine):
    inc = [IncomeStatement("CCC", "annual", 2023, revenue=10_000, net_income=1_000)]
    cf  = [CashFlowStatement("CCC", "annual", 2023, operating_cash_flow=1_200, free_cash_flow=800)]
    rev_proj = engine._project_revenues(inc, 2)
    fcfs = engine._project_free_cash_flows(inc, cf, rev_proj)
    assert len(fcfs) == 2
    assert all(f >= 0 for f in fcfs)