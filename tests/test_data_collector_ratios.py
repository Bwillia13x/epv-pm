import sys
from pathlib import Path
from datetime import date
import pytest  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from data.data_collector import DataCollector  # type: ignore
from models.financial_models import IncomeStatement, BalanceSheet  # type: ignore
from utils.cache_manager import CacheManager  # type: ignore


def _sample_statements():
    inc = [IncomeStatement("TST","annual",2023,net_income=1_000_000,revenue=4_000_000)]
    bal = [BalanceSheet("TST","annual",2023,total_equity=2_000_000,total_assets=3_000_000,
                        current_assets=1_000_000,current_liabilities=500_000,long_term_debt=700_000)]
    return inc, bal


def test_calculate_ratios_basic(monkeypatch):
    dc = DataCollector(CacheManager())
    income, balance = _sample_statements()
    data = {"symbol":"TST","income_statements":income,"balance_sheets":balance}
    ratios = dc._calculate_ratios(data)
    assert len(ratios) == 1
    r = ratios[0]
    # Simple ROE check: 1,000,000 / 2,000,000 *100 = 50
    assert pytest.approx(r.roe) == 50.0
    # Current ratio 1,000,000/500,000 = 2.0
    assert pytest.approx(r.current_ratio) == 2.0