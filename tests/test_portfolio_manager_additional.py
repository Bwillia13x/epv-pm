import sys
from pathlib import Path
import pytest  # type: ignore

# Add src to path
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT_DIR / "src"
if SRC_PATH.exists() and str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from analysis.portfolio_manager import PortfolioManager  # type: ignore



def _candidate(symbol: str, price: float, epv: float, quality: float, sector: str = "Technology"):
    return {
        "symbol": symbol,
        "current_price": price,
        "epv_per_share": epv,
        "quality_score": quality,
        "sector": sector,
        # Assume zero current weight for simplicity
        "current_weight": 0.0,
    }


@pytest.fixture

def sample_candidates():
    return [
        _candidate("AAA", 100.0, 130.0, 0.8, "Technology"),
        _candidate("BBB", 90.0, 80.0, 0.6, "Healthcare"),
        _candidate("CCC", 50.0, 70.0, 0.9, "Technology"),
    ]



def test_optimize_epv_quality_weights_sum(sample_candidates):
    """Optimised weights should sum to 1 and respect max position constraints."""
    manager = PortfolioManager()
    risk_budget = manager.create_risk_budget(max_position_size=0.7, max_sector_exposure=0.8)
    allocations = manager.optimize_portfolio(
        candidates=sample_candidates,
        portfolio_value=1_000_000,
        risk_budget=risk_budget,
        optimization_objective="max_epv_quality",
    )

    total_weight = sum(a.target_weight for a in allocations)
    # Weight totals may have minor floating error; allow small tolerance
    assert pytest.approx(total_weight, rel=1e-3) == 1.0

    # No weight should exceed the risk budget limit
    assert all(a.target_weight <= risk_budget.max_position_size + 1e-6 for a in allocations)

    # Recommended actions should be a subset of expected values
    valid_actions = {"BUY", "SELL", "HOLD"}
    assert set(a.recommended_action for a in allocations).issubset(valid_actions)

    # Conviction level should correlate with weight * quality
    for alloc in allocations:
        expected_conviction = alloc.target_weight * alloc.quality_score
        assert pytest.approx(alloc.conviction_level, rel=1e-6) == expected_conviction