import sys
from pathlib import Path
import pytest  # type: ignore
from datetime import date

# Ensure src on path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis.research_generator import ResearchGenerator  # type: ignore
from models.financial_models import (  # type: ignore
    CompanyProfile,
    EPVCalculation,
)


@pytest.fixture

def generator():
    return ResearchGenerator()


@pytest.fixture

def sample_company_data():
    profile = CompanyProfile(
        symbol="DEMO",
        company_name="Demo Corp",
        sector="Technology",
        description="A tech company",
    )
    return {"profile": profile}


@pytest.mark.parametrize(
    "mos,quality,risk,expected",[
        (30, 0.8, 0.3, "STRONG BUY"),
        (20, 0.6, 0.5, "BUY"),
        (10, 0.5, 0.7, "WEAK BUY"),
        (-5, 0.5, 0.5, "HOLD"),
        (-30, 0.9, 0.4, "WEAK SELL"),
    ],
)

def test_generate_recommendation(generator, mos, quality, risk, expected):
    epv = EPVCalculation(
        symbol="DEMO",
        calculation_date=date.today(),
        normalized_earnings=1_000_000,
        shares_outstanding=100_000,
        cost_of_capital=0.1,
        earnings_per_share=10.0,
        epv_per_share=100.0,
        epv_total=10_000_000,
        margin_of_safety=mos,
    )
    rec, _ = generator._generate_recommendation(epv, quality, risk)
    assert rec == expected


@pytest.mark.parametrize("quality,risk",[(0.9,0.3),(0.6,0.5),(0.4,0.8)])

def test_confidence_level_range(generator, quality, risk):
    conf = generator._calculate_confidence_level(quality, risk)
    assert 0.3 <= conf <= 0.95