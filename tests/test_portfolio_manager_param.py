import sys
from pathlib import Path
import numpy as np
import pytest  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.portfolio_manager import PortfolioManager  # type: ignore


@pytest.fixture
def pm():
    return PortfolioManager()


def test_estimate_volatilities_sector_defaults(pm):
    cands = [
        {"symbol": "AAA", "sector": "Technology"},
        {"symbol": "BBB", "sector": "Utilities"},
        {"symbol": "CCC"},  # Default sector
    ]
    vols = pm._estimate_volatilities(cands)
    assert pytest.approx(vols[0]) == 0.25
    assert pytest.approx(vols[1]) == 0.15
    assert pytest.approx(vols[2]) == 0.20


def test_estimate_correlation_same_sector(pm):
    c1 = {"symbol": "X", "sector": "Tech"}
    c2 = {"symbol": "Y", "sector": "Tech"}
    c3 = {"symbol": "Z", "sector": "Energy"}
    corr = pm._estimate_correlation_matrix([c1, c2, c3])
    # Same sector high correlation
    assert pytest.approx(corr[0][1]) == 0.6
    # Different sectors lower correlation
    assert pytest.approx(corr[0][2]) == 0.3


def test_optimize_minimum_variance(pm):
    # Simple 2-asset cov matrix with identical vols
    cov = np.array([[0.04, 0.02],[0.02,0.04]])
    rb = pm.create_risk_budget(max_position_size=1.0)
    weights = pm._optimize_minimum_variance(cov, rb)
    # For symmetric matrix, weights should be equal
    assert pytest.approx(weights[0], rel=1e-3) == 0.5
    assert pytest.approx(sum(weights)) == 1.0