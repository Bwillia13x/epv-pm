import numpy as np
import pytest
from datetime import date

from src.analysis.advanced_valuations import AdvancedValuationEngine
from src.models.financial_models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
)


@pytest.fixture(scope="module")
def engine() -> AdvancedValuationEngine:
    np.random.seed(0)
    return AdvancedValuationEngine()


def _gen_income(symbol: str):
    base_rev = 50_000_000
    base_inc = 5_000_000
    current_year = date.today().year
    stmts = []
    for i in range(3):
        y = current_year - i
        stmts.append(
            IncomeStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=y,
                revenue=base_rev * (1 + 0.05 * i),
                net_income=base_inc * (1 + 0.05 * i),
                eps=1.0,
                shares_outstanding=5_000_000,
            )
        )
    return stmts


def _gen_bs(symbol: str):
    current_year = date.today().year
    sheets = []
    for i in range(2):
        y = current_year - i
        sheets.append(
            BalanceSheet(
                symbol=symbol,
                period="annual",
                fiscal_year=y,
                total_assets=100_000_000,
                total_equity=60_000_000,
                long_term_debt=10_000_000,
                current_assets=30_000_000,
                current_liabilities=15_000_000,
                cash_and_equivalents=8_000_000,
            )
        )
    return sheets


def _gen_cf(symbol: str):
    current_year = date.today().year
    flows = []
    for i in range(2):
        y = current_year - i
        flows.append(
            CashFlowStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=y,
                operating_cash_flow=6_000_000,
                free_cash_flow=4_000_000,
                capital_expenditures=-2_000_000,
            )
        )
    return flows


def test_dcf_basic(engine: AdvancedValuationEngine):
    symbol = "TADV"
    inc = _gen_income(symbol)
    bs = _gen_bs(symbol)
    cf = _gen_cf(symbol)

    dcf = engine.calculate_dcf_valuation(
        symbol=symbol,
        income_statements=inc,
        balance_sheets=bs,
        cash_flow_statements=cf,
        projection_years=3,
    )

    assert dcf.dcf_per_share > 0
    # sanity: present value + terminal > 0
    assert dcf.enterprise_value > 0
    # sensitivity keys exist
    assert "discount_rate_sensitivity" in dcf.sensitivity_analysis


def test_monte_carlo_distribution(engine: AdvancedValuationEngine):
    symbol = "TADV"
    base = 10.0
    vol = {"revenue_growth": 0.01, "margin": 0.01, "multiple": 0.05}
    mc = engine.run_monte_carlo_simulation(symbol, base, vol, num_simulations=500)

    assert len(mc.value_distribution) == 500
    # mean should be near base
    assert abs(mc.mean_value - base) < base * 0.2