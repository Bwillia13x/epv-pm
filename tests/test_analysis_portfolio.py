import pytest
import numpy as np

from src.analysis.portfolio_manager import PortfolioManager


@pytest.fixture(scope="module")
def manager() -> PortfolioManager:
    return PortfolioManager()


def _sample_candidates():
    return [
        {
            "symbol": "AAA",
            "epv_per_share": 120.0,
            "current_price": 100.0,
            "quality_score": 0.8,
            "sector": "Technology",
        },
        {
            "symbol": "BBB",
            "epv_per_share": 80.0,
            "current_price": 90.0,
            "quality_score": 0.6,
            "sector": "Healthcare",
        },
        {
            "symbol": "CCC",
            "epv_per_share": 150.0,
            "current_price": 140.0,
            "quality_score": 0.9,
            "sector": "Technology",
        },
    ]


def test_optimize_portfolio_weights(manager: PortfolioManager):
    candidates = _sample_candidates()
    risk_budget = manager.create_risk_budget(max_position_size=0.5, max_sector_exposure=0.6)
    allocations = manager.optimize_portfolio(
        candidates=candidates,
        portfolio_value=1_000_000,
        risk_budget=risk_budget,
        optimization_objective="max_epv_quality",
    )

    # Check that allocations are within risk limits
    total_weight = sum(a.target_weight for a in allocations)
    assert abs(total_weight - 1.0) < 1e-6
    assert all(a.target_weight <= 0.5 + 1e-6 for a in allocations)

    # Basic sanity: allocations exist for all symbols
    symbols_in_alloc = {a.symbol for a in allocations}
    assert symbols_in_alloc == {"AAA", "BBB", "CCC"}


def test_risk_budget_creation(manager: PortfolioManager):
    rb = manager.create_risk_budget(max_position_size=0.2, max_sector_exposure=0.4)
    assert rb.max_position_size == 0.2
    assert rb.concentration_limits["sector_max"] == 0.4