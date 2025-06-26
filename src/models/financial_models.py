"""
Financial data models for the EPV Research Platform
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, date


@dataclass
class FinancialStatement:
    """Base class for financial statements"""

    symbol: str
    period: str  # 'annual' or 'quarterly'
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    report_date: Optional[date] = None
    filing_date: Optional[date] = None


@dataclass
class IncomeStatement(FinancialStatement):
    """Income statement data"""

    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    ebit: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    shares_outstanding: Optional[float] = None

    # Growth rates
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None


@dataclass
class BalanceSheet(FinancialStatement):
    """Balance sheet data"""

    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    inventory: Optional[float] = None
    receivables: Optional[float] = None

    total_liabilities: Optional[float] = None
    current_liabilities: Optional[float] = None
    long_term_debt: Optional[float] = None

    total_equity: Optional[float] = None
    retained_earnings: Optional[float] = None
    book_value_per_share: Optional[float] = None


@dataclass
class CashFlowStatement(FinancialStatement):
    """Cash flow statement data"""

    operating_cash_flow: Optional[float] = None
    investing_cash_flow: Optional[float] = None
    financing_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    capital_expenditures: Optional[float] = None
    dividends_paid: Optional[float] = None


@dataclass
class FinancialRatios:
    """Calculated financial ratios"""

    symbol: str
    calculation_date: date

    # Profitability ratios
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None

    # Liquidity ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None

    # Leverage ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    interest_coverage: Optional[float] = None

    # Efficiency ratios
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None


@dataclass
class MarketData:
    """Market data for a security"""

    symbol: str
    date: date
    price: float
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None


@dataclass
class EPVCalculation:
    """Earnings Power Value calculation results"""

    symbol: str
    calculation_date: date

    # Input data
    normalized_earnings: float
    shares_outstanding: float
    cost_of_capital: float

    # EPV components
    earnings_per_share: float
    epv_per_share: float
    epv_total: float

    # Current market comparison
    current_price: Optional[float] = None
    margin_of_safety: Optional[float] = None

    # Quality assessment
    quality_score: Optional[float] = None
    quality_components: Dict[str, float] = field(default_factory=dict)

    # Growth scenarios
    growth_scenarios: Dict[str, float] = field(default_factory=dict)
    investment_thesis: Optional[str] = None
    risk_factors: Optional[List[str]] = None


@dataclass
class CompanyProfile:
    """Company profile and fundamental data"""

    symbol: str
    company_name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None

    # Business description
    description: Optional[str] = None
    employees: Optional[int] = None
    founded: Optional[int] = None

    # Key metrics
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    trailing_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None

    # Dividends
    dividend_rate: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None

    # Last updated
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ResearchReport:
    """Comprehensive research report for a company"""

    symbol: str
    company_name: str
    report_date: date

    # Company profile
    profile: CompanyProfile

    # Financial data (last 5-10 years)
    income_statements: List[IncomeStatement] = field(default_factory=list)
    balance_sheets: List[BalanceSheet] = field(default_factory=list)
    cash_flow_statements: List[CashFlowStatement] = field(default_factory=list)

    # Calculated ratios
    financial_ratios: List[FinancialRatios] = field(default_factory=list)

    # Market data
    current_market_data: Optional[MarketData] = None
    historical_prices: List[MarketData] = field(default_factory=list)

    # EPV Analysis
    epv_calculation: Optional[EPVCalculation] = None

    # Quality assessment
    quality_score: Optional[float] = None
    quality_analysis: Dict[str, Any] = field(default_factory=dict)

    # Competitive analysis
    peer_comparisons: Dict[str, Any] = field(default_factory=dict)

    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    risk_score: Optional[float] = None

    # Summary and recommendation
    investment_thesis: Optional[str] = None
    recommendation: Optional[str] = None  # BUY, HOLD, SELL
    target_price: Optional[float] = None

    # Metadata
    generated_by: str = "EPV Research Platform"
    confidence_level: Optional[float] = None


class PortfolioPosition:
    """Portfolio position tracking"""

    def __init__(
        self,
        symbol: str,
        shares: float,
        avg_cost: float,
        current_price: float,
        epv_per_share: float,
    ):
        self.symbol = symbol
        self.shares = shares
        self.avg_cost = avg_cost
        self.current_price = current_price
        self.epv_per_share = epv_per_share

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_cost

    @property
    def unrealized_gain_loss(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def unrealized_return_pct(self) -> float:
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_gain_loss / self.cost_basis) * 100

    @property
    def epv_total(self) -> float:
        return self.shares * self.epv_per_share

    @property
    def epv_margin_of_safety(self) -> float:
        if self.current_price == 0:
            return 0.0
        return ((self.epv_per_share - self.current_price) / self.current_price) * 100
