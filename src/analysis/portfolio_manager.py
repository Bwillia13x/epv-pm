"""
Portfolio Management and Optimization
Advanced portfolio construction, risk management, and performance attribution
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import date
import logging
from dataclasses import dataclass
from scipy.optimize import minimize
import warnings

warnings.filterwarnings("ignore")

from src.models.financial_models import MarketData, PortfolioPosition

# mypy: ignore-errors


@dataclass
class PortfolioAllocation:
    """Portfolio allocation recommendation"""

    symbol: str
    target_weight: float
    current_weight: float
    recommended_action: str  # BUY, SELL, HOLD
    shares_to_trade: float
    dollar_amount: float

    # Rationale
    epv_per_share: float
    current_price: float
    margin_of_safety: float
    quality_score: float
    conviction_level: float


@dataclass
class PortfolioMetrics:
    """Portfolio performance and risk metrics"""

    portfolio_value: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float

    # Risk metrics
    portfolio_beta: float
    tracking_error: Optional[float]
    value_at_risk_5pct: float
    expected_shortfall: float

    # EPV-specific metrics
    weighted_epv: float
    weighted_margin_of_safety: float
    weighted_quality_score: float
    epv_to_market_ratio: float


@dataclass
class RiskBudget:
    """Risk budgeting allocation"""

    total_risk_budget: float
    sector_allocations: Dict[str, float]
    position_limits: Dict[str, float]
    concentration_limits: Dict[str, float]

    # Risk constraints
    max_position_size: float
    max_sector_exposure: float
    max_single_stock_risk: float
    target_tracking_error: Optional[float]


@dataclass
class RebalancingRecommendation:
    """Portfolio rebalancing recommendations"""

    rebalance_date: date
    current_allocations: Dict[str, float]
    target_allocations: Dict[str, float]
    trades_required: List[PortfolioAllocation]

    # Metrics
    current_deviation: float
    rebalancing_cost: float
    expected_improvement: float

    # Timing
    days_since_last_rebalance: int
    trigger_reason: str


class PortfolioManager:
    """
    Advanced portfolio management system with EPV-based optimization
    """

    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        self.logger = logging.getLogger(__name__)

    def optimize_portfolio(
        self,
        candidates: List[Dict],
        portfolio_value: float,
        risk_budget: RiskBudget,
        optimization_objective: str = "max_epv_quality",
    ) -> List[PortfolioAllocation]:
        """
        Optimize portfolio allocation based on EPV and quality metrics

        Args:
            candidates: List of investment candidates with EPV data
            portfolio_value: Total portfolio value
            risk_budget: Risk budgeting constraints
            optimization_objective: 'max_epv_quality', 'max_sharpe', 'min_variance'

        Returns:
            List of recommended portfolio allocations
        """

        self.logger.info(f"Optimizing portfolio with {len(candidates)} candidates")

        try:
            # Prepare optimization data
            symbols = [c["symbol"] for c in candidates]
            epv_values = np.array([c.get("epv_per_share", 0) for c in candidates])
            current_prices = np.array([c.get("current_price", 1) for c in candidates])
            quality_scores = np.array([c.get("quality_score", 0.5) for c in candidates])

            # Calculate expected returns (based on EPV vs current price)
            expected_returns = np.array(
                [
                    max(0, (epv - price) / price) if price > 0 else 0
                    for epv, price in zip(epv_values, current_prices)
                ]
            )

            # Estimate correlation matrix (simplified - would use historical data in practice)
            
            correlation_matrix = self._estimate_correlation_matrix(candidates)

            # Estimate volatilities (simplified)
            volatilities = self._estimate_volatilities(candidates)

            # Calculate covariance matrix
            cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix

            # Set up optimization
            if optimization_objective == "max_epv_quality":
                weights = self._optimize_epv_quality(
                    expected_returns, quality_scores, cov_matrix, risk_budget
                )
            elif optimization_objective == "max_sharpe":
                weights = self._optimize_sharpe_ratio(
                    expected_returns, cov_matrix, risk_budget
                )
            elif optimization_objective == "min_variance":
                weights = self._optimize_minimum_variance(cov_matrix, risk_budget)
            else:
                raise ValueError(
                    f"Unknown optimization objective: {optimization_objective}"
                )

            # Create allocation recommendations
            allocations = []
            for i, (symbol, weight) in enumerate(zip(symbols, weights)):
                if weight > 0.01:  # Only include meaningful allocations
                    candidate = candidates[i]

                    dollar_amount = portfolio_value * weight
                    shares_to_trade = (
                        dollar_amount / current_prices[i]
                        if current_prices[i] > 0
                        else 0
                    )

                    # Determine action
                    current_weight = candidate.get("current_weight", 0)
                    if weight > current_weight + 0.01:
                        action = "BUY"
                    elif weight < current_weight - 0.01:
                        action = "SELL"
                    else:
                        action = "HOLD"

                    allocation = PortfolioAllocation(
                        symbol=symbol,
                        target_weight=weight,
                        current_weight=current_weight,
                        recommended_action=action,
                        shares_to_trade=abs(shares_to_trade),
                        dollar_amount=abs(dollar_amount),
                        epv_per_share=epv_values[i],
                        current_price=current_prices[i],
                        margin_of_safety=(
                            (epv_values[i] - current_prices[i])
                            / current_prices[i]
                            * 100
                            if current_prices[i] > 0
                            else 0
                        ),
                        quality_score=quality_scores[i],
                        conviction_level=weight
                        * quality_scores[i],  # Weight by quality
                    )

                    allocations.append(allocation)

            # Sort by conviction level
            allocations.sort(key=lambda x: x.conviction_level, reverse=True)

            self.logger.info(
                f"Portfolio optimization complete: {len(allocations)} positions recommended"
            )
            return allocations

        except Exception as e:
            self.logger.error(f"Error optimizing portfolio: {e}")
            raise

    def calculate_portfolio_metrics(
        self,
        positions: List[PortfolioPosition],
        historical_prices: Dict[str, List[MarketData]],
        benchmark_returns: Optional[List[float]] = None,
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""

        self.logger.info(
            f"Calculating metrics for portfolio with {len(positions)} positions"
        )

        try:
            # Calculate portfolio value and weights
            total_value = sum(pos.market_value for pos in positions)
            weights = (
                [pos.market_value / total_value for pos in positions]
                if total_value > 0
                else []
            )

            # Calculate returns
            portfolio_returns = self._calculate_portfolio_returns(
                positions, historical_prices
            )

            if len(portfolio_returns) == 0:
                raise ValueError("No historical data available for portfolio metrics")

            # Performance metrics
            total_return = (
                (portfolio_returns[-1] - portfolio_returns[0]) / portfolio_returns[0]
                if len(portfolio_returns) > 1
                else 0
            )

            # Annualized return (assuming daily data)
            days = len(portfolio_returns)
            annualized_return = (
                (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
            )

            # Volatility
            daily_returns = np.diff(portfolio_returns) / portfolio_returns[:-1]
            volatility = (
                np.std(daily_returns) * np.sqrt(252) if len(daily_returns) > 1 else 0
            )

            # Sharpe ratio
            excess_return = annualized_return - self.risk_free_rate
            sharpe_ratio = excess_return / volatility if volatility > 0 else 0

            # Maximum drawdown
            peak = np.maximum.accumulate(portfolio_returns)
            drawdown = (portfolio_returns - peak) / peak
            max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0

            # Risk metrics
            portfolio_beta = self._calculate_portfolio_beta(
                daily_returns, benchmark_returns
            )
            tracking_error = self._calculate_tracking_error(
                daily_returns, benchmark_returns
            )

            # Value at Risk (5%)
            var_5pct = (
                np.percentile(daily_returns, 5) * np.sqrt(252)
                if len(daily_returns) > 0
                else 0
            )

            # Expected Shortfall (Conditional VaR)
            expected_shortfall = (
                np.mean(daily_returns[daily_returns <= np.percentile(daily_returns, 5)])
                * np.sqrt(252)
                if len(daily_returns) > 0
                else 0
            )

            # EPV-specific metrics
            weighted_epv = sum(
                pos.epv_per_share * weight for pos, weight in zip(positions, weights)
            )
            weighted_margin_of_safety = sum(
                pos.epv_margin_of_safety * weight
                for pos, weight in zip(positions, weights)
            )

            # Quality score (would need to be passed in or calculated)
            weighted_quality_score = 0.7  # Placeholder

            # EPV to market ratio
            weighted_market_price = sum(
                pos.current_price * weight for pos, weight in zip(positions, weights)
            )
            epv_to_market_ratio = (
                weighted_epv / weighted_market_price if weighted_market_price > 0 else 0
            )

            return PortfolioMetrics(
                portfolio_value=total_value,
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                portfolio_beta=portfolio_beta,
                tracking_error=tracking_error,
                value_at_risk_5pct=var_5pct,
                expected_shortfall=expected_shortfall,
                weighted_epv=weighted_epv,
                weighted_margin_of_safety=weighted_margin_of_safety,
                weighted_quality_score=weighted_quality_score,
                epv_to_market_ratio=epv_to_market_ratio,
            )

        except Exception as e:
            self.logger.error(f"Error calculating portfolio metrics: {e}")
            raise

    def generate_rebalancing_recommendation(
        self,
        current_positions: List[PortfolioPosition],
        target_allocations: List[PortfolioAllocation],
        rebalancing_threshold: float = 0.05,
        transaction_cost: float = 0.001,
    ) -> Optional[RebalancingRecommendation]:
        """Generate rebalancing recommendations"""

        self.logger.info("Generating rebalancing recommendations")

        try:
            # Calculate current allocations
            total_value = sum(pos.market_value for pos in current_positions)
            current_allocations = {
                pos.symbol: pos.market_value / total_value
                for pos in current_positions
                if total_value > 0
            }

            # Calculate target allocations
            target_allocations_dict = {
                alloc.symbol: alloc.target_weight for alloc in target_allocations
            }

            # Calculate deviations
            deviations = {}
            for symbol in set(
                list(current_allocations.keys()) + list(target_allocations_dict.keys())
            ):
                current = current_allocations.get(symbol, 0)
                target = target_allocations_dict.get(symbol, 0)
                deviations[symbol] = abs(current - target)

            # Check if rebalancing is needed
            max_deviation = max(deviations.values()) if deviations else 0

            if max_deviation < rebalancing_threshold:
                self.logger.info(
                    f"No rebalancing needed (max deviation: {max_deviation:.1%})"
                )
                return None

            # Generate trades
            trades_required = []
            total_trade_value = 0

            for alloc in target_allocations:
                current_weight = current_allocations.get(alloc.symbol, 0)
                weight_diff = alloc.target_weight - current_weight

                if abs(weight_diff) > rebalancing_threshold:
                    dollar_amount = abs(weight_diff * total_value)
                    total_trade_value += dollar_amount

                    trade = PortfolioAllocation(
                        symbol=alloc.symbol,
                        target_weight=alloc.target_weight,
                        current_weight=current_weight,
                        recommended_action="BUY" if weight_diff > 0 else "SELL",
                        shares_to_trade=(
                            dollar_amount / alloc.current_price
                            if alloc.current_price > 0
                            else 0
                        ),
                        dollar_amount=dollar_amount,
                        epv_per_share=alloc.epv_per_share,
                        current_price=alloc.current_price,
                        margin_of_safety=alloc.margin_of_safety,
                        quality_score=alloc.quality_score,
                        conviction_level=alloc.conviction_level,
                    )

                    trades_required.append(trade)

            # Calculate costs and benefits
            rebalancing_cost = total_trade_value * transaction_cost
            expected_improvement = self._estimate_rebalancing_benefit(
                current_allocations, target_allocations_dict
            )

            # Determine trigger reason
            trigger_reason = f"Maximum deviation ({max_deviation:.1%}) exceeds threshold ({rebalancing_threshold:.1%})"

            return RebalancingRecommendation(
                rebalance_date=date.today(),
                current_allocations=current_allocations,
                target_allocations=target_allocations_dict,
                trades_required=trades_required,
                current_deviation=max_deviation,
                rebalancing_cost=rebalancing_cost,
                expected_improvement=expected_improvement,
                days_since_last_rebalance=30,  # Would track this in practice
                trigger_reason=trigger_reason,
            )

        except Exception as e:
            self.logger.error(f"Error generating rebalancing recommendation: {e}")
            raise

    def create_risk_budget(
        self,
        target_volatility: float = 0.15,
        max_position_size: float = 0.1,
        max_sector_exposure: float = 0.3,
    ) -> RiskBudget:
        """Create risk budget with constraints"""

        return RiskBudget(
            total_risk_budget=target_volatility,
            sector_allocations={
                "Technology": 0.25,
                "Healthcare": 0.20,
                "Financial": 0.15,
                "Consumer": 0.15,
                "Industrial": 0.10,
                "Other": 0.15,
            },
            position_limits={
                "single_position": max_position_size,
                "top_5_positions": 0.4,
                "top_10_positions": 0.6,
            },
            concentration_limits={
                "sector_max": max_sector_exposure,
                "country_max": 0.5,
                "currency_max": 0.6,
            },
            max_position_size=max_position_size,
            max_sector_exposure=max_sector_exposure,
            max_single_stock_risk=0.05,
            target_tracking_error=0.03,
        )

    def _optimize_epv_quality(
        self,
        expected_returns: np.ndarray,
        quality_scores: np.ndarray,
        cov_matrix: np.ndarray,
        risk_budget: RiskBudget,
    ) -> np.ndarray:
        """Optimize for EPV-adjusted quality"""

        n_assets = len(expected_returns)

        # Objective: maximize quality-adjusted expected returns minus risk penalty
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_quality = np.dot(weights, quality_scores)
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

            # Quality-adjusted return with risk penalty
            risk_penalty = 2.0  # Risk aversion parameter
            return -(
                portfolio_return * portfolio_quality - risk_penalty * portfolio_risk
            )

        # Constraints
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # Weights sum to 1
        ]

        # Bounds
        bounds = [(0, risk_budget.max_position_size) for _ in range(n_assets)]

        # Initial guess
        x0 = np.ones(n_assets) / n_assets

        # Optimize
        result = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )

        return result.x if result.success else x0

    def _optimize_sharpe_ratio(
        self,
        expected_returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_budget: RiskBudget,
    ) -> np.ndarray:
        """Optimize for maximum Sharpe ratio"""

        n_assets = len(expected_returns)

        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

            # Negative Sharpe ratio (to minimize)
            if portfolio_risk == 0:
                return -np.inf
            return -(portfolio_return - self.risk_free_rate) / portfolio_risk

        # Constraints and bounds
        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0, risk_budget.max_position_size) for _ in range(n_assets)]
        x0 = np.ones(n_assets) / n_assets

        result = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )

        return result.x if result.success else x0

    def _optimize_minimum_variance(
        self, cov_matrix: np.ndarray, risk_budget: RiskBudget
    ) -> np.ndarray:
        """Optimize for minimum variance"""

        n_assets = cov_matrix.shape[0]

        def objective(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))

        constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
        bounds = [(0, risk_budget.max_position_size) for _ in range(n_assets)]
        x0 = np.ones(n_assets) / n_assets

        result = minimize(
            objective, x0, method="SLSQP", bounds=bounds, constraints=constraints
        )

        return result.x if result.success else x0

    def _estimate_correlation_matrix(self, candidates: List[Dict]) -> np.ndarray:
        """Estimate correlation matrix (simplified)"""

        n = len(candidates)

        # Create a simple correlation matrix
        # In practice, this would use historical price data
        correlation = np.eye(n)

        # Add some cross-correlations based on sectors
        for i in range(n):
            for j in range(i + 1, n):
                # Same sector = higher correlation
                sector_i = candidates[i].get("sector", "Unknown")
                sector_j = candidates[j].get("sector", "Unknown")

                if sector_i == sector_j:
                    correlation[i, j] = correlation[j, i] = 0.6
                else:
                    correlation[i, j] = correlation[j, i] = 0.3

        return correlation

    def _estimate_volatilities(self, candidates: List[Dict]) -> np.ndarray:
        """Estimate volatilities (simplified)"""

        # Default volatilities by sector
        sector_volatilities = {
            "Technology": 0.25,
            "Healthcare": 0.20,
            "Financial": 0.30,
            "Consumer": 0.18,
            "Industrial": 0.22,
            "Energy": 0.35,
            "Utilities": 0.15,
            "Default": 0.20,
        }

        volatilities = []
        for candidate in candidates:
            sector = candidate.get("sector", "Default")
            vol = sector_volatilities.get(sector, sector_volatilities["Default"])
            volatilities.append(vol)

        return np.array(volatilities)

    def _calculate_portfolio_returns(
        self,
        positions: List[PortfolioPosition],
        historical_prices: Dict[str, List[MarketData]],
    ) -> List[float]:
        """Calculate historical portfolio returns"""

        if not historical_prices:
            return []

        # Get common date range
        all_dates = set()
        for symbol_prices in historical_prices.values():
            all_dates.update(price.date for price in symbol_prices)

        common_dates = sorted(list(all_dates))

        if len(common_dates) < 2:
            return []

        # Calculate portfolio values over time
        portfolio_values = []

        for date_point in common_dates:
            daily_value = 0

            for position in positions:
                symbol = position.symbol
                if symbol in historical_prices:
                    # Find price for this date
                    day_price = next(
                        (
                            p.price
                            for p in historical_prices[symbol]
                            if p.date == date_point
                        ),
                        None,
                    )

                    if day_price:
                        daily_value += position.shares * day_price

            if daily_value > 0:
                portfolio_values.append(daily_value)

        return portfolio_values

    def _calculate_portfolio_beta(
        self, portfolio_returns: np.ndarray, benchmark_returns: Optional[List[float]]
    ) -> float:
        """Calculate portfolio beta"""

        if benchmark_returns is None or len(benchmark_returns) != len(
            portfolio_returns
        ):
            return 1.0  # Default beta

        if len(portfolio_returns) < 2:
            return 1.0

        try:
            covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)

            return covariance / benchmark_variance if benchmark_variance > 0 else 1.0
        except Exception as e:
            self.logger.error(f"Error calculating portfolio beta: {e}")
            return 1.0

    def _calculate_tracking_error(
        self, portfolio_returns: np.ndarray, benchmark_returns: Optional[List[float]]
    ) -> Optional[float]:
        """Calculate tracking error"""

        if benchmark_returns is None or len(benchmark_returns) != len(
            portfolio_returns
        ):
            return None

        if len(portfolio_returns) < 2:
            return None

        try:
            excess_returns = portfolio_returns - np.array(benchmark_returns)
            return np.std(excess_returns) * np.sqrt(252)  # Annualized
        except:
            return None

    def _estimate_rebalancing_benefit(
        self,
        current_allocations: Dict[str, float],
        target_allocations: Dict[str, float],
    ) -> float:
        """Estimate benefit of rebalancing (simplified)"""

        # Calculate allocation efficiency improvement
        total_deviation = sum(
            abs(target_allocations.get(symbol, 0) - current_allocations.get(symbol, 0))
            for symbol in set(
                list(current_allocations.keys()) + list(target_allocations.keys())
            )
        )

        # Estimate annual benefit as percentage of deviation reduced
        estimated_annual_benefit = total_deviation * 0.02  # 2% per unit of deviation

        return estimated_annual_benefit
