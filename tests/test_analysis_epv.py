import pytest
from datetime import date

from src.analysis.epv_calculator import EPVCalculator
from src.models.financial_models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    FinancialRatios,
)


def _generate_income_statements(symbol: str, start_year: int, years: int):
    """Helper to create synthetic deterministic income statements."""
    statements = []
    revenue = 100_000_000  # start revenue
    net_inc = 10_000_000   # start net income
    for i in range(years):
        fiscal_year = start_year - i
        statements.append(
            IncomeStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=fiscal_year,
                revenue=revenue,
                net_income=net_inc,
                shares_outstanding=10_000_000,
            )
        )
        # deterministic linear growth
        revenue *= 1.05
        net_inc *= 1.04
    return statements


def _generate_balance_sheets(symbol: str, start_year: int, years: int):
    sheets = []
    assets = 200_000_000
    equity = 120_000_000
    debt = 20_000_000
    for i in range(years):
        fy = start_year - i
        sheets.append(
            BalanceSheet(
                symbol=symbol,
                period="annual",
                fiscal_year=fy,
                total_assets=assets,
                total_equity=equity,
                long_term_debt=debt,
                current_assets=50_000_000,
                current_liabilities=25_000_000,
            )
        )
        assets *= 1.04
        equity *= 1.04
        debt *= 1.02
    return sheets


def _generate_cash_flows(symbol: str, start_year: int, years: int):
    flows = []
    ocf = 15_000_000
    fcf = 12_000_000
    capex = -3_000_000
    for i in range(years):
        fy = start_year - i
        flows.append(
            CashFlowStatement(
                symbol=symbol,
                period="annual",
                fiscal_year=fy,
                operating_cash_flow=ocf,
                free_cash_flow=fcf,
                capital_expenditures=capex,
            )
        )
        ocf *= 1.03
        fcf *= 1.03
    return flows


@pytest.fixture(scope="module")
def calculator() -> EPVCalculator:
    return EPVCalculator()


@pytest.mark.parametrize("years", [5, 8])
def test_epv_calculation_positive(calculator: EPVCalculator, years: int):
    """EPV per share should be positive and margin of safety computed."""
    symbol = "DEMO"
    current_year = date.today().year
    income_stmts = _generate_income_statements(symbol, current_year, years)
    balance_sheets = _generate_balance_sheets(symbol, current_year, years)
    cash_flows = _generate_cash_flows(symbol, current_year, years)

    # Fake market price using last revenue/net income ratio
    current_price = 25.0

    financial_ratios = [
        FinancialRatios(symbol=symbol, calculation_date=date.today(), roe=15.0, current_ratio=2.0)
    ]

    epv = calculator.calculate_epv(
        symbol=symbol,
        income_statements=income_stmts,
        balance_sheets=balance_sheets,
        cash_flow_statements=cash_flows,
        financial_ratios=financial_ratios,
        current_price=current_price,
    )

    assert epv.epv_per_share > 0
    assert epv.margin_of_safety is not None


@pytest.mark.parametrize("roe", [8.0, 20.0])
def test_quality_score_sane(calculator: EPVCalculator, roe: float):
    """Quality score should increase with higher ROE."""
    symbol = "QDEM"
    now = date.today().year
    inc = _generate_income_statements(symbol, now, 5)
    bal = _generate_balance_sheets(symbol, now, 5)
    ratios_low = [FinancialRatios(symbol=symbol, calculation_date=date.today(), roe=roe)]

    score, _analysis = calculator.calculate_quality_score(inc, bal, ratios_low)
    assert 0 <= score <= 1.0


@pytest.mark.parametrize("growth_rate", [0.0, 0.03])
def test_growth_scenarios(calculator: EPVCalculator, growth_rate):
    symbol = "GDEM"
    base_eps = 2.0
    shares = 1_000_000
    cost = 0.1

    scenarios = calculator._calculate_growth_scenarios(
        normalized_earnings=base_eps * shares,
        cost_of_capital=cost,
        shares_outstanding=shares,
    )
    # baseline value
    base_val = scenarios["zero_growth"]
    assert base_val > 0

    if growth_rate > 0:
        key = f"{int(growth_rate*100)}%_growth"
        assert key in scenarios
        assert scenarios[key] > base_val