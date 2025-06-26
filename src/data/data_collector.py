"""
Data collection module for the EPV Research Platform
Integrates multiple data sources for comprehensive financial analysis
"""

import yfinance as yf
import asyncio
import httpx
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import time
import logging
from abc import ABC, abstractmethod

from src.models.financial_models import (
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    MarketData,
    CompanyProfile,
    FinancialRatios,
)
from src.utils.cache_manager import CacheManager
from src.utils.rate_limiter import RateLimiter


class DataSource(ABC):
    """Abstract base class for data sources"""

    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self.rate_limiter = rate_limiter or RateLimiter()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        pass

    @abstractmethod
    async def get_financial_statements(
        self, symbol: str, years: int = 5
    ) -> Tuple[List, List, List]:
        pass

    @abstractmethod
    async def get_market_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[MarketData]:
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Optional[Dict]:
        pass


class AlphaVantageSource(DataSource):
    """Alpha Vantage data source implementation"""

    def __init__(self, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(rate_limiter)
        self.api_key = api_key

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        return None

    async def get_financial_statements(
        self, symbol: str, years: int = 5
    ) -> Tuple[List, List, List]:
        return [], [], []

    async def get_market_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[MarketData]:
        return []

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get the latest quote from Alpha Vantage."""
        try:
            self.rate_limiter.wait_if_needed()
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                quote = data.get("Global Quote")
                if quote:
                    return {
                        "symbol": quote["01. symbol"],
                        "price": float(quote["05. price"]),
                        "timestamp": datetime.now(),
                        "provider": "AlphaVantage",
                    }
                return None
        except Exception as e:
            self.logger.error(
                f"Error fetching quote for {symbol} from Alpha Vantage: {e}"
            )
            return None


class FredSource(DataSource):
    """FRED data source implementation"""

    def __init__(self, api_key: str, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(rate_limiter)
        self.api_key = api_key

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        return None

    async def get_financial_statements(
        self, symbol: str, years: int = 5
    ) -> Tuple[List, List, List]:
        return [], [], []

    async def get_market_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[MarketData]:
        return []

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Get the latest quote from FRED."""
        # FRED does not provide real-time stock quotes
        return None


class YahooFinanceSource(DataSource):
    """Yahoo Finance data source implementation"""

    def __init__(
        self,
        rate_limiter: Optional[RateLimiter] = None,
        session: Optional[requests.Session] = None,
    ):
        super().__init__(rate_limiter)
        self.session = session

    async def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile from Yahoo Finance asynchronously (non-blocking)."""

        def _fetch_profile() -> Optional[CompanyProfile]:
            try:
                ticker = yf.Ticker(symbol, session=self.session)
                info = ticker.info  # type: ignore[attr-defined]  # blocking network call

                if not info or "shortName" not in info:
                    return None

                return CompanyProfile(
                    symbol=symbol,
                    company_name=info.get("shortName", ""),
                    sector=info.get("sector"),
                    industry=info.get("industry"),
                    country=info.get("country"),
                    exchange=info.get("exchange"),
                    currency=info.get("currency"),
                    description=info.get("longBusinessSummary"),
                    employees=info.get("fullTimeEmployees"),
                    market_cap=info.get("marketCap"),
                    enterprise_value=info.get("enterpriseValue"),
                    trailing_pe=info.get("trailingPE"),
                    forward_pe=info.get("forwardPE"),
                    peg_ratio=info.get("pegRatio"),
                    dividend_rate=info.get("dividendRate"),
                    dividend_yield=info.get("dividendYield"),
                    payout_ratio=info.get("payoutRatio"),
                )
            except Exception as exc:  # pragma: no cover – depends on upstream site
                self.logger.error(f"Error fetching profile for {symbol}: {exc}")
                return None

        # ensure we respect rate-limits before scheduling thread-work
        self.rate_limiter.wait_if_needed()
        return await asyncio.to_thread(_fetch_profile)

    async def get_financial_statements(
        self, symbol: str, years: int = 5
    ) -> Tuple[List, List, List]:
        """Get annual financial statements asynchronously using thread pool."""

        def _sync_fetch():  # noqa: C901 – uses heavy yfinance logic
            try:
                ticker = yf.Ticker(symbol, session=self.session)
                income_stmt = ticker.financials  # type: ignore[attr-defined]
                balance_sheet = ticker.balance_sheet  # type: ignore[attr-defined]
                cash_flow = ticker.cashflow  # type: ignore[attr-defined]

                income_statements, balance_sheets, cash_flow_statements = [], [], []

                if income_stmt is not None and not income_stmt.empty:
                    for col in income_stmt.columns[:years]:
                        fiscal_year = col.year
                        stmt = IncomeStatement(
                            symbol=symbol,
                            period="annual",
                            fiscal_year=fiscal_year,
                            report_date=col.date(),
                            revenue=self._safe_get(income_stmt, "Total Revenue", col),
                            gross_profit=self._safe_get(
                                income_stmt, "Gross Profit", col
                            ),
                            operating_income=self._safe_get(
                                income_stmt, "Operating Income", col
                            ),
                            ebit=self._safe_get(income_stmt, "EBIT", col),
                            ebitda=self._safe_get(income_stmt, "EBITDA", col),
                            net_income=self._safe_get(income_stmt, "Net Income", col),
                        )
                        income_statements.append(stmt)

                if balance_sheet is not None and not balance_sheet.empty:
                    for col in balance_sheet.columns[:years]:
                        fiscal_year = col.year
                        bs = BalanceSheet(
                            symbol=symbol,
                            period="annual",
                            fiscal_year=fiscal_year,
                            report_date=col.date(),
                            total_assets=self._safe_get(
                                balance_sheet, "Total Assets", col
                            ),
                            current_assets=self._safe_get(
                                balance_sheet, "Current Assets", col
                            ),
                            cash_and_equivalents=self._safe_get(
                                balance_sheet, "Cash And Cash Equivalents", col
                            ),
                            inventory=self._safe_get(balance_sheet, "Inventory", col),
                            receivables=self._safe_get(
                                balance_sheet, "Net Receivables", col
                            ),
                            total_liabilities=self._safe_get(
                                balance_sheet, "Total Liab", col
                            ),
                            current_liabilities=self._safe_get(
                                balance_sheet, "Current Liabilities", col
                            ),
                            long_term_debt=self._safe_get(
                                balance_sheet, "Long Term Debt", col
                            ),
                            total_equity=self._safe_get(
                                balance_sheet, "Total Stockholder Equity", col
                            ),
                        )
                        balance_sheets.append(bs)

                if cash_flow is not None and not cash_flow.empty:
                    for col in cash_flow.columns[:years]:
                        fiscal_year = col.year
                        cf = CashFlowStatement(
                            symbol=symbol,
                            period="annual",
                            fiscal_year=fiscal_year,
                            report_date=col.date(),
                            operating_cash_flow=self._safe_get(
                                cash_flow, "Total Cash From Operating Activities", col
                            ),
                            investing_cash_flow=self._safe_get(
                                cash_flow,
                                "Total Cashflows From Investing Activities",
                                col,
                            ),
                            financing_cash_flow=self._safe_get(
                                cash_flow, "Total Cash From Financing Activities", col
                            ),
                            capital_expenditures=self._safe_get(
                                cash_flow, "Capital Expenditures", col
                            ),
                            free_cash_flow=self._calculate_free_cash_flow(
                                cash_flow, col
                            ),
                        )
                        cash_flow_statements.append(cf)

                return income_statements, balance_sheets, cash_flow_statements
            except Exception as exc:
                self.logger.error(
                    f"Error fetching financial statements for {symbol}: {exc}"
                )
                return [], [], []

        self.rate_limiter.wait_if_needed()
        return await asyncio.to_thread(_sync_fetch)

    async def get_market_data(
        self, symbol: str, start_date: date, end_date: date
    ) -> List[MarketData]:
        """Get historical OHLC data asynchronously (threaded)."""

        def _sync_hist():
            try:
                ticker = yf.Ticker(symbol, session=self.session)
                return ticker.history(start=start_date, end=end_date)  # type: ignore[attr-defined]
            except Exception as exc:
                self.logger.error(f"Error fetching hist for {symbol}: {exc}")
                return None

        self.rate_limiter.wait_if_needed()
        hist = await asyncio.to_thread(_sync_hist)

        market_data: List[MarketData] = []
        if hist is None or hist.empty:
            return market_data

        for idx, row in hist.iterrows():
            market_data.append(
                MarketData(
                    symbol=symbol,
                    date=idx.date(),
                    price=row["Close"],
                    volume=int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                )
            )
        return market_data

    async def get_quote(self, symbol: str) -> Optional[Dict]:
        """Fast, non-blocking latest quote via thread off-loading."""

        def _sync_quote():
            try:
                ticker = yf.Ticker(symbol, session=self.session)
                info = ticker.info  # type: ignore[attr-defined]
                if info and info.get("regularMarketPrice"):
                    return {
                        "symbol": symbol,
                        "price": info["regularMarketPrice"],
                        "timestamp": datetime.now(),
                        "provider": "YahooFinance",
                    }
            except Exception as exc:
                self.logger.error(
                    f"Error fetching quote for {symbol} from Yahoo Finance: {exc}"
                )
            return None

        self.rate_limiter.wait_if_needed()
        return await asyncio.to_thread(_sync_quote)

    def _safe_get(self, df: pd.DataFrame, key: str, column) -> Optional[float]:
        """Safely get value from DataFrame"""
        try:
            if key in df.index:
                value = df.loc[key, column]
                return float(value) if pd.notna(value) else None
            return None
        except Exception as exc:
            self.logger.error(f"Error fetching hist for {symbol}: {exc}")
            return None

    def _calculate_free_cash_flow(
        self, cash_flow: pd.DataFrame, column
    ) -> Optional[float]:
        """Calculate free cash flow"""
        try:
            ocf = self._safe_get(
                cash_flow, "Total Cash From Operating Activities", column
            )
            capex = self._safe_get(cash_flow, "Capital Expenditures", column)

            if ocf is not None and capex is not None:
                return ocf + capex  # capex is usually negative
            return None
        except Exception as exc:
            self.logger.error(f"Error fetching hist for {symbol}: {exc}")
            return None


class DataCollector:
    """Main data collection orchestrator – now supports fully async collection."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()
        self.rate_limiter = RateLimiter(requests_per_minute=30)

        # Initialize data sources
        self.yahoo_finance = YahooFinanceSource(self.rate_limiter)

        self.logger = logging.getLogger(__name__)

    # ---------------------------------------------------------------------
    # Public async API
    # ---------------------------------------------------------------------
    async def collect_company_data_async(self, symbol: str, years: int = 10) -> Dict:
        """Async version of `collect_company_data` – non-blocking end-to-end."""

        self.logger.info(f"Collecting data for {symbol} (async)")

        cache_key = f"company_data_{symbol}_{years}y"
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            self.logger.info(f"Using cached data for {symbol} (cache hit)")
            return cached_data

        data: Dict = {
            "symbol": symbol,
            "collection_date": datetime.now(),
            "company_profile": None,
            "income_statements": [],
            "balance_sheets": [],
            "cash_flow_statements": [],
            "market_data": [],
            "financial_ratios": [],
            "current_price": None,
            "market_cap": None,
        }

        # Gather async provider requests concurrently for best latency
        profile_task = asyncio.create_task(
            self.yahoo_finance.get_company_profile(symbol)
        )
        financials_task = asyncio.create_task(
            self.yahoo_finance.get_financial_statements(symbol, years)
        )

        # Market data (last 2y) – can run in parallel as well
        end_date = date.today()
        start_date = end_date - timedelta(days=730)
        market_task = asyncio.create_task(
            self.yahoo_finance.get_market_data(symbol, start_date, end_date)
        )

        # Await all
        data["company_profile"] = await profile_task
        income_stmts, balance_sheets, cash_flows = await financials_task
        data["income_statements"] = income_stmts
        data["balance_sheets"] = balance_sheets
        data["cash_flow_statements"] = cash_flows

        data["market_data"] = await market_task

        # Current price from latest market data
        if data["market_data"]:
            data["current_price"] = data["market_data"][-1].price

        # Calculate financial ratios synchronously (CPU-bound)
        data["financial_ratios"] = self._calculate_ratios(data)

        # Cache
        self.cache_manager.set(cache_key, data)
        self.logger.info(f"Data collection complete for {symbol} (async)")
        return data

    # ---------------------------------------------------------------------
    # Legacy synchronous wrappers (keep API compatibility)
    # ---------------------------------------------------------------------
    def collect_company_data(self, symbol: str, years: int = 10) -> Dict:  # noqa: D401
        """Synchronous wrapper for code paths still expecting blocking call."""
        return asyncio.run(self.collect_company_data_async(symbol, years))

    # ---------------------------------------------------------------------
    # Convenience aliases
    # ---------------------------------------------------------------------
    async def collect_comprehensive_data_async(self, symbol: str, years: int = 10):
        """Async alias returning SimpleNamespace like the legacy sync variant."""
        import types

        result = await self.collect_company_data_async(symbol, years)
        return types.SimpleNamespace(**result)

    def collect_comprehensive_data(self, symbol: str, years: int = 10):  # type: ignore[override]
        """Synchronous alias maintained for backward compatibility."""
        import types

        return types.SimpleNamespace(**self.collect_company_data(symbol, years))

    def _calculate_ratios(self, data: Dict) -> List[FinancialRatios]:
        """Calculate financial ratios from collected data"""
        ratios = []

        try:
            income_stmts = data["income_statements"]
            balance_sheets = data["balance_sheets"]

            # Match statements by fiscal year
            for income_stmt in income_stmts:
                matching_bs = next(
                    (
                        bs
                        for bs in balance_sheets
                        if bs.fiscal_year == income_stmt.fiscal_year
                    ),
                    None,
                )

                if matching_bs and income_stmt.net_income and matching_bs.total_equity:
                    ratio = FinancialRatios(
                        symbol=data["symbol"], calculation_date=date.today()
                    )

                    # Calculate profitability ratios
                    if income_stmt.net_income and matching_bs.total_equity:
                        ratio.roe = (
                            income_stmt.net_income / matching_bs.total_equity
                        ) * 100

                    if income_stmt.net_income and matching_bs.total_assets:
                        ratio.roa = (
                            income_stmt.net_income / matching_bs.total_assets
                        ) * 100

                    if income_stmt.revenue and income_stmt.gross_profit:
                        ratio.gross_margin = (
                            income_stmt.gross_profit / income_stmt.revenue
                        ) * 100

                    if income_stmt.revenue and income_stmt.operating_income:
                        ratio.operating_margin = (
                            income_stmt.operating_income / income_stmt.revenue
                        ) * 100

                    if income_stmt.revenue and income_stmt.net_income:
                        ratio.net_margin = (
                            income_stmt.net_income / income_stmt.revenue
                        ) * 100

                    # Calculate liquidity ratios
                    if matching_bs.current_assets and matching_bs.current_liabilities:
                        ratio.current_ratio = (
                            matching_bs.current_assets / matching_bs.current_liabilities
                        )

                    # Calculate leverage ratios
                    if matching_bs.long_term_debt and matching_bs.total_equity:
                        ratio.debt_to_equity = (
                            matching_bs.long_term_debt / matching_bs.total_equity
                        )

                    ratios.append(ratio)

        except Exception as e:
            self.logger.error(f"Error calculating ratios: {e}")

        return ratios

    def get_peer_comparison_data(self, symbol: str, peer_symbols: List[str]) -> Dict:
        """Get comparative data for peer analysis"""
        comparison_data = {"target": symbol, "peers": {}}

        # Get target company data
        target_data = self.collect_company_data(symbol, years=5)
        comparison_data["target_data"] = target_data

        # Get peer data
        for peer_symbol in peer_symbols:
            try:
                peer_data = self.collect_company_data(peer_symbol, years=5)
                comparison_data["peers"][peer_symbol] = peer_data
                time.sleep(1)  # Rate limiting
            except Exception as e:
                self.logger.error(f"Error collecting peer data for {peer_symbol}: {e}")

        return comparison_data
