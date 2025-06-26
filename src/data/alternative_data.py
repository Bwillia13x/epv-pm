"""
Alternative Data Sources and Intelligence
Integrates SEC filings, insider trading, ESG data, sentiment analysis, and management assessment
"""

import numpy as np
from typing import Dict, List, Optional, Union
from datetime import date, datetime, timedelta
import logging
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class SECFiling:
    """SEC filing data structure"""

    symbol: str
    filing_type: str  # 10-K, 10-Q, 8-K, etc.
    filing_date: date
    period_end_date: Optional[date]
    accession_number: str

    # Content analysis
    document_url: str
    key_metrics: Dict[str, Union[float, str]] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    management_discussion: str = ""

    # Sentiment and flags
    sentiment_score: Optional[float] = None
    red_flags: List[str] = field(default_factory=list)
    positive_signals: List[str] = field(default_factory=list)


@dataclass
class InsiderTrading:
    """Insider trading transaction"""

    symbol: str
    insider_name: str
    title: str
    transaction_date: date
    transaction_type: str  # Buy, Sell
    shares_transacted: float
    price_per_share: float
    shares_owned_after: float

    # Analysis
    transaction_value: float
    ownership_change_pct: float
    significance_score: float  # 0-1 scale


@dataclass
class ESGScoring:
    """ESG (Environmental, Social, Governance) scoring"""

    symbol: str
    assessment_date: date

    # Individual scores (0-100)
    environmental_score: Optional[float]
    social_score: Optional[float]
    governance_score: Optional[float]
    overall_esg_score: Optional[float]

    # Risk factors
    esg_risk_factors: List[str] = field(default_factory=list)
    esg_opportunities: List[str] = field(default_factory=list)

    # Ratings
    esg_rating: Optional[str] = None  # AAA, AA, A, BBB, etc.
    controversy_level: Optional[str] = None  # High, Medium, Low


@dataclass
class SentimentAnalysis:
    """News and social media sentiment analysis"""

    symbol: str
    analysis_date: date

    # Sentiment scores (-1 to 1)
    news_sentiment: Optional[float]
    social_sentiment: Optional[float]
    analyst_sentiment: Optional[float]
    overall_sentiment: Optional[float]

    # Volume metrics
    news_volume: int = 0
    social_mentions: int = 0
    analyst_updates: int = 0

    # Key themes
    positive_themes: List[str] = field(default_factory=list)
    negative_themes: List[str] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)


@dataclass
class ManagementAssessment:
    """Management quality and track record assessment"""

    symbol: str
    assessment_date: date

    # Key executives
    ceo_name: str
    ceo_tenure_years: Optional[float]
    cfo_name: str
    cfo_tenure_years: Optional[float]

    # Track record metrics
    historical_performance_score: Optional[float]  # 0-1 scale
    capital_allocation_score: Optional[float]
    strategic_execution_score: Optional[float]

    # Red flags
    governance_issues: List[str] = field(default_factory=list)
    compensation_concerns: List[str] = field(default_factory=list)

    # Positive factors
    leadership_strengths: List[str] = field(default_factory=list)
    strategic_initiatives: List[str] = field(default_factory=list)


class AlternativeDataProvider(ABC):
    """Abstract base class for alternative data providers"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def collect_data(self, symbol: str) -> Dict:
        pass


class SECDataProvider(AlternativeDataProvider):
    """SEC filings data provider"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://data.sec.gov"

    def collect_data(self, symbol: str) -> Dict[str, List[SECFiling]]:
        """Collect SEC filings for a symbol"""

        self.logger.info(f"Collecting SEC filings for {symbol}")

        try:
            filings = self._get_recent_filings(symbol)

            # Analyze each filing
            analyzed_filings = []
            for filing in filings:
                analyzed_filing = self._analyze_filing(filing)
                analyzed_filings.append(analyzed_filing)

            return {"sec_filings": analyzed_filings}

        except Exception as e:
            self.logger.error(f"Error collecting SEC data for {symbol}: {e}")
            return {"sec_filings": []}

    def _get_recent_filings(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get recent filings from SEC EDGAR database"""

        # Mock data - in practice would use SEC API
        mock_filings = [
            {
                "symbol": symbol,
                "filing_type": "10-K",
                "filing_date": date.today() - timedelta(days=90),
                "period_end_date": date.today() - timedelta(days=180),
                "accession_number": f"{symbol}-10K-2023",
                "document_url": f"https://sec.gov/filings/{symbol}-10K-2023.htm",
            },
            {
                "symbol": symbol,
                "filing_type": "10-Q",
                "filing_date": date.today() - timedelta(days=30),
                "period_end_date": date.today() - timedelta(days=90),
                "accession_number": f"{symbol}-10Q-Q3-2023",
                "document_url": f"https://sec.gov/filings/{symbol}-10Q-Q3-2023.htm",
            },
        ]

        return mock_filings[:limit]

    def _analyze_filing(self, filing_data: Dict) -> SECFiling:
        """Analyze individual SEC filing"""

        # Extract key information (mock analysis)
        key_metrics = {
            "revenue_growth": 0.05,  # 5% growth
            "margin_improvement": 0.02,  # 2% margin improvement
            "debt_level": "Moderate",
            "guidance_provided": True,
        }

        # Mock risk factor extraction
        risk_factors = [
            "Competitive market pressures",
            "Regulatory changes",
            "Economic uncertainty",
            "Technology disruption risks",
        ]

        # Mock red flag detection
        red_flags = []
        if filing_data["filing_type"] == "8-K":
            red_flags.append("Unscheduled filing - potential material event")

        # Mock sentiment analysis
        sentiment_score = np.random.uniform(-0.2, 0.3)  # Slightly positive bias

        return SECFiling(
            symbol=filing_data["symbol"],
            filing_type=filing_data["filing_type"],
            filing_date=filing_data["filing_date"],
            period_end_date=filing_data.get("period_end_date"),
            accession_number=filing_data["accession_number"],
            document_url=filing_data["document_url"],
            key_metrics=key_metrics,
            risk_factors=risk_factors,
            management_discussion="Management remains optimistic about growth prospects...",
            sentiment_score=sentiment_score,
            red_flags=red_flags,
            positive_signals=["Strong cash flow generation", "Market share expansion"],
        )


class InsiderTradingProvider(AlternativeDataProvider):
    """Insider trading data provider"""

    def collect_data(self, symbol: str) -> Dict[str, List[InsiderTrading]]:
        """Collect insider trading data"""

        self.logger.info(f"Collecting insider trading data for {symbol}")

        try:
            # Mock insider trading data
            insider_transactions = self._get_insider_transactions(symbol)

            return {"insider_trading": insider_transactions}

        except Exception as e:
            self.logger.error(
                f"Error collecting insider trading data for {symbol}: {e}"
            )
            return {"insider_trading": []}

    def _get_insider_transactions(
        self, symbol: str, days_back: int = 90
    ) -> List[InsiderTrading]:
        """Get recent insider transactions"""

        # Mock data generation
        transactions = []

        for i in range(np.random.randint(0, 5)):  # 0-4 transactions
            transaction_date = date.today() - timedelta(
                days=np.random.randint(1, days_back)
            )
            shares_transacted = np.random.randint(1000, 50000)
            price_per_share = np.random.uniform(50, 300)
            transaction_type = np.random.choice(
                ["Buy", "Sell"], p=[0.3, 0.7]
            )  # More sells than buys

            transaction = InsiderTrading(
                symbol=symbol,
                insider_name=f"John Doe {i+1}",
                title=np.random.choice(["CEO", "CFO", "COO", "Director", "VP"]),
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                shares_transacted=shares_transacted,
                price_per_share=price_per_share,
                shares_owned_after=shares_transacted * np.random.uniform(2, 10),
                transaction_value=shares_transacted * price_per_share,
                ownership_change_pct=np.random.uniform(5, 25),
                significance_score=np.random.uniform(0.3, 0.9),
            )

            transactions.append(transaction)

        return transactions


class ESGDataProvider(AlternativeDataProvider):
    """ESG scoring data provider"""

    def collect_data(self, symbol: str) -> Dict[str, ESGScoring]:
        """Collect ESG scoring data"""

        self.logger.info(f"Collecting ESG data for {symbol}")

        try:
            esg_data = self._get_esg_scores(symbol)

            return {"esg_scoring": esg_data}

        except Exception as e:
            self.logger.error(f"Error collecting ESG data for {symbol}: {e}")
            return {"esg_scoring": None}

    def _get_esg_scores(self, symbol: str) -> ESGScoring:
        """Get ESG scores and analysis"""

        # Mock ESG scores
        environmental_score = np.random.uniform(40, 85)
        social_score = np.random.uniform(45, 90)
        governance_score = np.random.uniform(50, 95)
        overall_score = (environmental_score + social_score + governance_score) / 3

        # Determine rating
        if overall_score >= 80:
            rating = "AAA"
        elif overall_score >= 70:
            rating = "AA"
        elif overall_score >= 60:
            rating = "A"
        elif overall_score >= 50:
            rating = "BBB"
        else:
            rating = "BB"

        return ESGScoring(
            symbol=symbol,
            assessment_date=date.today(),
            environmental_score=environmental_score,
            social_score=social_score,
            governance_score=governance_score,
            overall_esg_score=overall_score,
            esg_risk_factors=[
                "Carbon emissions exposure",
                "Water usage concerns",
                "Labor practices review needed",
            ],
            esg_opportunities=[
                "Renewable energy transition",
                "Diversity and inclusion programs",
                "Supply chain sustainability",
            ],
            esg_rating=rating,
            controversy_level="Low" if overall_score > 70 else "Medium",
        )


class SentimentDataProvider(AlternativeDataProvider):
    """News and social sentiment data provider"""

    def collect_data(self, symbol: str) -> Dict[str, SentimentAnalysis]:
        """Collect sentiment analysis data"""

        self.logger.info(f"Collecting sentiment data for {symbol}")

        try:
            sentiment_data = self._analyze_sentiment(symbol)

            return {"sentiment_analysis": sentiment_data}

        except Exception as e:
            self.logger.error(f"Error collecting sentiment data for {symbol}: {e}")
            return {"sentiment_analysis": None}

    def _analyze_sentiment(self, symbol: str) -> SentimentAnalysis:
        """Analyze news and social sentiment"""

        # Mock sentiment scores
        news_sentiment = np.random.uniform(-0.3, 0.4)
        social_sentiment = np.random.uniform(-0.5, 0.5)
        analyst_sentiment = np.random.uniform(-0.2, 0.3)

        overall_sentiment = (
            news_sentiment * 0.4 + social_sentiment * 0.3 + analyst_sentiment * 0.3
        )

        return SentimentAnalysis(
            symbol=symbol,
            analysis_date=date.today(),
            news_sentiment=news_sentiment,
            social_sentiment=social_sentiment,
            analyst_sentiment=analyst_sentiment,
            overall_sentiment=overall_sentiment,
            news_volume=np.random.randint(5, 50),
            social_mentions=np.random.randint(100, 5000),
            analyst_updates=np.random.randint(1, 10),
            positive_themes=[
                "Strong earnings outlook",
                "New product launches",
                "Market expansion",
            ],
            negative_themes=[
                "Competitive pressures",
                "Regulatory concerns",
                "Cost inflation",
            ],
            trending_topics=[
                "Digital transformation",
                "ESG initiatives",
                "Supply chain optimization",
            ],
        )


class ManagementDataProvider(AlternativeDataProvider):
    """Management assessment data provider"""

    def collect_data(self, symbol: str) -> Dict[str, ManagementAssessment]:
        """Collect management assessment data"""

        self.logger.info(f"Collecting management data for {symbol}")

        try:
            management_data = self._assess_management(symbol)

            return {"management_assessment": management_data}

        except Exception as e:
            self.logger.error(f"Error collecting management data for {symbol}: {e}")
            return {"management_assessment": None}

    def _assess_management(self, symbol: str) -> ManagementAssessment:
        """Assess management quality and track record"""

        # Mock management assessment
        ceo_tenure = np.random.uniform(2, 15)
        cfo_tenure = np.random.uniform(1, 10)

        # Calculate scores based on tenure and performance
        historical_performance = min(0.9, 0.4 + (ceo_tenure * 0.05))
        capital_allocation = np.random.uniform(0.3, 0.8)
        strategic_execution = np.random.uniform(0.4, 0.9)

        return ManagementAssessment(
            symbol=symbol,
            assessment_date=date.today(),
            ceo_name="Jane Smith",
            ceo_tenure_years=ceo_tenure,
            cfo_name="Bob Johnson",
            cfo_tenure_years=cfo_tenure,
            historical_performance_score=historical_performance,
            capital_allocation_score=capital_allocation,
            strategic_execution_score=strategic_execution,
            governance_issues=(
                [] if capital_allocation > 0.6 else ["Executive compensation concerns"]
            ),
            compensation_concerns=(
                []
                if historical_performance > 0.6
                else ["Pay-for-performance alignment"]
            ),
            leadership_strengths=[
                "Strong industry experience",
                "Clear strategic vision",
                "Effective capital allocation",
            ],
            strategic_initiatives=[
                "Digital transformation program",
                "Operational efficiency improvements",
                "Market expansion strategy",
            ],
        )


class AlternativeDataCollector:
    """
    Main coordinator for alternative data collection
    """

    def __init__(self):
        self.sec_provider = SECDataProvider()
        self.insider_provider = InsiderTradingProvider()
        self.esg_provider = ESGDataProvider()
        self.sentiment_provider = SentimentDataProvider()
        self.management_provider = ManagementDataProvider()
        self.logger = logging.getLogger(__name__)

    def collect_comprehensive_data(self, symbol: str) -> Dict:
        """Collect all alternative data for a symbol"""

        self.logger.info(f"Collecting comprehensive alternative data for {symbol}")

        comprehensive_data = {
            "symbol": symbol,
            "collection_date": datetime.now(),
            "data_sources": {},
        }

        # Collect from all providers
        providers = [
            ("sec_filings", self.sec_provider),
            ("insider_trading", self.insider_provider),
            ("esg_data", self.esg_provider),
            ("sentiment_data", self.sentiment_provider),
            ("management_data", self.management_provider),
        ]

        for data_type, provider in providers:
            try:
                data = provider.collect_data(symbol)
                comprehensive_data["data_sources"][data_type] = data
                self.logger.debug(f"Collected {data_type} for {symbol}")
            except Exception as e:
                self.logger.error(f"Failed to collect {data_type} for {symbol}: {e}")
                comprehensive_data["data_sources"][data_type] = {}

        # Generate composite intelligence scores
        comprehensive_data["intelligence_scores"] = self._calculate_intelligence_scores(
            comprehensive_data["data_sources"]
        )

        return comprehensive_data

    def _calculate_intelligence_scores(self, data_sources: Dict) -> Dict[str, float]:
        """Calculate composite intelligence scores from all data sources"""

        scores = {}

        try:
            # ESG score
            esg_data = data_sources.get("esg_data", {}).get("esg_scoring")
            if esg_data:
                scores["esg_score"] = (
                    esg_data.overall_esg_score / 100
                    if esg_data.overall_esg_score
                    else 0.5
                )
            else:
                scores["esg_score"] = 0.5

            # Sentiment score (normalized to 0-1)
            sentiment_data = data_sources.get("sentiment_data", {}).get(
                "sentiment_analysis"
            )
            if sentiment_data and sentiment_data.overall_sentiment is not None:
                scores["sentiment_score"] = (
                    sentiment_data.overall_sentiment + 1
                ) / 2  # Convert from -1,1 to 0,1
            else:
                scores["sentiment_score"] = 0.5

            # Management quality score
            mgmt_data = data_sources.get("management_data", {}).get(
                "management_assessment"
            )
            if mgmt_data:
                mgmt_scores = [
                    mgmt_data.historical_performance_score or 0.5,
                    mgmt_data.capital_allocation_score or 0.5,
                    mgmt_data.strategic_execution_score or 0.5,
                ]
                scores["management_score"] = np.mean(mgmt_scores)
            else:
                scores["management_score"] = 0.5

            # Insider trading score (based on recent activity)
            insider_data = data_sources.get("insider_trading", {}).get(
                "insider_trading", []
            )
            if insider_data:
                recent_buys = [t for t in insider_data if t.transaction_type == "Buy"]
                recent_sells = [t for t in insider_data if t.transaction_type == "Sell"]

                buy_signal = len(recent_buys) / max(1, len(insider_data))
                sell_signal = len(recent_sells) / max(1, len(insider_data))

                scores["insider_trading_score"] = (
                    buy_signal - sell_signal * 0.5 + 0.5
                )  # Normalize
            else:
                scores["insider_trading_score"] = 0.5

            # SEC filing quality score
            sec_data = data_sources.get("sec_filings", {}).get("sec_filings", [])
            if sec_data:
                sentiment_scores = [
                    f.sentiment_score for f in sec_data if f.sentiment_score is not None
                ]
                if sentiment_scores:
                    avg_sentiment = np.mean(sentiment_scores)
                    scores["filing_quality_score"] = (
                        avg_sentiment + 1
                    ) / 2  # Normalize
                else:
                    scores["filing_quality_score"] = 0.5
            else:
                scores["filing_quality_score"] = 0.5

            # Overall alternative data score
            score_values = list(scores.values())
            scores["overall_alternative_score"] = (
                np.mean(score_values) if score_values else 0.5
            )

        except Exception as e:
            self.logger.error(f"Error calculating intelligence scores: {e}")
            # Return default scores
            scores = {
                "esg_score": 0.5,
                "sentiment_score": 0.5,
                "management_score": 0.5,
                "insider_trading_score": 0.5,
                "filing_quality_score": 0.5,
                "overall_alternative_score": 0.5,
            }

        return scores

    def get_red_flags(self, symbol: str, data_sources: Dict) -> List[str]:
        """Extract red flags from all data sources"""

        red_flags = []

        try:
            # SEC filing red flags
            sec_data = data_sources.get("sec_filings", {}).get("sec_filings", [])
            for filing in sec_data:
                red_flags.extend(filing.red_flags)

            # Management red flags
            mgmt_data = data_sources.get("management_data", {}).get(
                "management_assessment"
            )
            if mgmt_data:
                red_flags.extend(mgmt_data.governance_issues)
                red_flags.extend(mgmt_data.compensation_concerns)

            # ESG red flags
            esg_data = data_sources.get("esg_data", {}).get("esg_scoring")
            if esg_data and esg_data.controversy_level == "High":
                red_flags.append("High ESG controversy level")

            # Insider trading red flags
            insider_data = data_sources.get("insider_trading", {}).get(
                "insider_trading", []
            )
            heavy_selling = [
                t
                for t in insider_data
                if t.transaction_type == "Sell" and t.significance_score > 0.7
            ]
            if len(heavy_selling) > 2:
                red_flags.append("Multiple significant insider sales")

            # Sentiment red flags
            sentiment_data = data_sources.get("sentiment_data", {}).get(
                "sentiment_analysis"
            )
            if (
                sentiment_data
                and sentiment_data.overall_sentiment
                and sentiment_data.overall_sentiment < -0.3
            ):
                red_flags.append("Persistently negative sentiment")

        except Exception as e:
            self.logger.error(f"Error extracting red flags for {symbol}: {e}")

        return list(set(red_flags))  # Remove duplicates
