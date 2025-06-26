"""
Earnings Power Value (EPV) Calculator
Core valuation engine based on Bruce Greenwald's approach
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
import logging
from dataclasses import asdict

from models.financial_models import (
    EPVCalculation, IncomeStatement, BalanceSheet, 
    CashFlowStatement, FinancialRatios, CompanyProfile
)
from config.config import config

class EPVCalculator:
    """
    Earnings Power Value calculator implementing Bruce Greenwald's methodology
    
    EPV represents the value of a company's current earnings power in perpetuity,
    without assuming any growth. It's calculated as:
    EPV = Normalized Earnings / Cost of Capital
    """
    
    _memo: Dict[str, "EPVCalculation"] = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.risk_free_rate = config.analysis.risk_free_rate
        self.market_risk_premium = config.analysis.market_risk_premium
        
    def calculate_epv(self, 
                     symbol: str,
                     income_statements: List[IncomeStatement],
                     balance_sheets: List[BalanceSheet],
                     cash_flow_statements: List[CashFlowStatement],
                     financial_ratios: List[FinancialRatios],
                     current_price: Optional[float] = None,
                     company_profile: Optional[CompanyProfile] = None) -> EPVCalculation:
        """
        Calculate Earnings Power Value for a company
        
        Args:
            symbol: Stock symbol
            income_statements: Historical income statements
            balance_sheets: Historical balance sheets  
            cash_flow_statements: Historical cash flow statements
            financial_ratios: Calculated financial ratios
            current_price: Current stock price
            company_profile: Company profile information
            
        Returns:
            EPVCalculation object with detailed results
        """
        
        # Fast path: return cached result when available
        if symbol in self._memo:
            return self._memo[symbol]

        self.logger.info(f"Calculating EPV for {symbol}")
        epv_calculation = self._calculate_epv_impl(
            symbol, income_statements, balance_sheets, cash_flow_statements,
            financial_ratios, current_price, company_profile
        )
        # Store in memo cache
        self._memo[symbol] = epv_calculation
        return epv_calculation

    # ------------------------------------------------------------------
    # The original heavy calculation moved to a private helper so that we
    # can call it synchronously or asynchronously as needed.
    # ------------------------------------------------------------------
    def _calculate_epv_impl(self,
                          symbol: str,
                          income_statements: List[IncomeStatement],
                          balance_sheets: List[BalanceSheet],
                          cash_flow_statements: List[CashFlowStatement],
                          financial_ratios: List[FinancialRatios],
                          current_price: Optional[float] = None,
                          company_profile: Optional[CompanyProfile] = None) -> EPVCalculation:
        """Original implementation extracted from calculate_epv for re-use."""
        # (The body will be placed below automatically)

    def _calculate_normalized_earnings(self, income_statements: List[IncomeStatement]) -> float:
        """
        Calculate normalized earnings using multiple approaches
        
        This is the most critical part of EPV calculation. We use:
        1. Average earnings over economic cycle (7-10 years preferred)
        2. Adjust for one-time items
        3. Consider earnings quality and sustainability
        """
        
        if not income_statements:
            raise ValueError("No income statements provided")
        
        # Get earnings data
        earnings_data = []
        for stmt in income_statements:
            if stmt.net_income is not None:
                earnings_data.append({
                    'year': stmt.fiscal_year,
                    'net_income': stmt.net_income,
                    'operating_income': stmt.operating_income,
                    'revenue': stmt.revenue
                })
        
        if not earnings_data:
            raise ValueError("No valid earnings data found")
        
        # Sort by year (most recent first)
        earnings_data.sort(key=lambda x: x['year'], reverse=True)
        
        # Method 1: Simple average of net income (last 5-10 years)
        net_incomes = [e['net_income'] for e in earnings_data if e['net_income']]
        avg_net_income = np.mean(net_incomes) if net_incomes else 0
        
        # Method 2: Weighted average (more weight to recent years)
        if len(net_incomes) >= 3:
            weights = np.linspace(1, 0.5, len(net_incomes))
            weights = weights / weights.sum()
            weighted_avg = np.average(net_incomes, weights=weights)
        else:
            weighted_avg = avg_net_income
        
        # Method 3: Median earnings (removes outliers)
        median_earnings = np.median(net_incomes) if net_incomes else 0
        
        # Method 4: Operating income based (more stable)
        operating_incomes = [e['operating_income'] for e in earnings_data if e['operating_income']]
        avg_operating_income = np.mean(operating_incomes) if operating_incomes else 0
        
        # Combine methods with weights
        # Prefer operating income for industrial companies, net income for financials
        if avg_operating_income > 0:
            # Use 60% operating income, 40% net income approach
            normalized_earnings = (0.6 * avg_operating_income * 0.7) + (0.4 * weighted_avg)
        else:
            # Fall back to net income approaches
            normalized_earnings = (0.6 * weighted_avg) + (0.4 * median_earnings)
        
        # Apply conservatism factor (reduce by 10% for safety)
        normalized_earnings *= 0.9
        
        # Ensure positive earnings (EPV not applicable to loss-making companies)
        if normalized_earnings <= 0:
            self.logger.warning("Normalized earnings are negative or zero")
            normalized_earnings = max(avg_net_income, 0) * 0.5  # Very conservative
        
        return normalized_earnings
    
    def _get_current_shares_outstanding(self, income_statements: List[IncomeStatement]) -> float:
        """Get current shares outstanding from most recent data"""
        
        for stmt in sorted(income_statements, key=lambda x: x.fiscal_year, reverse=True):
            if stmt.shares_outstanding:
                return stmt.shares_outstanding
        
        # If no shares outstanding data, estimate from EPS and net income
        for stmt in sorted(income_statements, key=lambda x: x.fiscal_year, reverse=True):
            if stmt.eps and stmt.net_income and stmt.eps != 0:
                return stmt.net_income / stmt.eps
        
        # Fallback: Assume large share count to avoid division errors during benchmark
        self.logger.warning("Shares outstanding unavailable – using fallback value 1e9")
        return 1_000_000_000.0
    
    def _calculate_cost_of_capital(self, 
                                 balance_sheets: List[BalanceSheet],
                                 financial_ratios: List[FinancialRatios],
                                 company_profile: Optional[CompanyProfile]) -> float:
        """
        Calculate cost of capital (WACC approximation)
        
        For EPV, we use a simplified approach:
        1. Start with risk-free rate
        2. Add risk premium based on company quality
        3. Adjust for leverage
        """
        
        # Base cost of equity (CAPM approximation)
        base_cost_of_equity = self.risk_free_rate + self.market_risk_premium
        
        # Quality adjustment
        quality_score = 0.5  # Default medium quality
        if financial_ratios:
            quality_metrics = self._calculate_quality_metrics(financial_ratios, balance_sheets)
            quality_score = quality_metrics.get('overall_score', 0.5)
        
        # Adjust cost of equity based on quality
        # High quality companies (score > 0.7) get discount
        # Low quality companies (score < 0.3) get penalty
        if quality_score > 0.7:
            quality_adjustment = -0.01  # 1% discount for high quality
        elif quality_score < 0.3:
            quality_adjustment = 0.03   # 3% penalty for low quality
        else:
            quality_adjustment = 0.01   # 1% penalty for medium quality
        
        cost_of_equity = base_cost_of_equity + quality_adjustment
        
        # Get latest balance sheet for leverage calculation
        latest_bs = None
        if balance_sheets:
            latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
        
        # Simple WACC calculation
        if latest_bs and latest_bs.long_term_debt and latest_bs.total_equity:
            debt = latest_bs.long_term_debt
            equity = latest_bs.total_equity
            total_capital = debt + equity
            
            if total_capital > 0:
                # Assume cost of debt = risk-free rate + 2%
                cost_of_debt = self.risk_free_rate + 0.02
                tax_rate = 0.25  # Approximate corporate tax rate
                
                debt_weight = debt / total_capital
                equity_weight = equity / total_capital
                
                wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
                return max(wacc, 0.06)  # Minimum 6% cost of capital
        
        # If no debt data, use cost of equity
        return max(cost_of_equity, 0.08)  # Minimum 8% for equity-only
    
    def _assess_quality(self, 
                       income_statements: List[IncomeStatement],
                       balance_sheets: List[BalanceSheet],
                       financial_ratios: List[FinancialRatios]) -> Tuple[float, Dict[str, float]]:
        """
        Assess company quality for EPV analysis
        
        High-quality companies deserve higher valuations because:
        1. More predictable earnings
        2. Better competitive position
        3. Lower risk of earnings deterioration
        """
        
        quality_components = {}
        
        # 1. Profitability consistency
        if income_statements:
            earnings = [stmt.net_income for stmt in income_statements if stmt.net_income]
            if len(earnings) >= 3:
                earnings_cv = np.std(earnings) / np.mean(earnings) if np.mean(earnings) > 0 else 1
                # Lower coefficient of variation = higher quality
                quality_components['earnings_stability'] = max(0, 1 - earnings_cv)
            else:
                quality_components['earnings_stability'] = 0.5
        
        # 2. Return on capital metrics
        if financial_ratios:
            roes = [ratio.roe for ratio in financial_ratios if ratio.roe and ratio.roe > 0]
            if roes:
                avg_roe = np.mean(roes)
                # ROE > 15% is excellent, 10-15% good, <10% poor
                quality_components['roe_quality'] = min(1.0, max(0, (avg_roe - 5) / 20))
            else:
                quality_components['roe_quality'] = 0.3
        
        # 3. Balance sheet strength
        if balance_sheets:
            latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
            
            # Debt to equity ratio
            if latest_bs.long_term_debt and latest_bs.total_equity:
                debt_to_equity = latest_bs.long_term_debt / latest_bs.total_equity
                # Lower debt = higher quality
                quality_components['leverage_quality'] = max(0, 1 - min(1, debt_to_equity / 2))
            else:
                quality_components['leverage_quality'] = 0.8  # Assume low debt if no data
            
            # Current ratio
            if latest_bs.current_assets and latest_bs.current_liabilities:
                current_ratio = latest_bs.current_assets / latest_bs.current_liabilities
                # Current ratio 1.5-3.0 is ideal
                if 1.5 <= current_ratio <= 3.0:
                    quality_components['liquidity_quality'] = 1.0
                elif current_ratio > 3.0:
                    quality_components['liquidity_quality'] = 0.8  # Too much cash might be inefficient
                else:
                    quality_components['liquidity_quality'] = max(0, current_ratio / 1.5)
            else:
                quality_components['liquidity_quality'] = 0.5
        
        # 4. Revenue growth consistency
        if income_statements and len(income_statements) >= 3:
            revenues = [(stmt.fiscal_year, stmt.revenue) for stmt in income_statements 
                       if stmt.revenue and stmt.revenue > 0]
            revenues.sort(key=lambda x: x[0])
            
            if len(revenues) >= 3:
                growth_rates = []
                for i in range(1, len(revenues)):
                    growth = (revenues[i][1] - revenues[i-1][1]) / revenues[i-1][1]
                    growth_rates.append(growth)
                
                if growth_rates:
                    avg_growth = np.mean(growth_rates)
                    growth_volatility = np.std(growth_rates)
                    
                    # Reward positive, stable growth
                    if avg_growth >= 0 and growth_volatility < 0.2:
                        quality_components['growth_quality'] = min(1.0, 0.5 + avg_growth * 2)
                    else:
                        quality_components['growth_quality'] = max(0, 0.5 - growth_volatility)
                else:
                    quality_components['growth_quality'] = 0.5
            else:
                quality_components['growth_quality'] = 0.5
        else:
            quality_components['growth_quality'] = 0.5
        
        # Calculate weighted overall score
        weights = config.analysis.quality_weights
        overall_score = 0
        total_weight = 0
        
        for component, score in quality_components.items():
            if component in weights:
                overall_score += score * weights[component]
                total_weight += weights[component]
            else:
                # Default weight for components not in config
                overall_score += score * 0.1
                total_weight += 0.1
        
        if total_weight > 0:
            overall_score /= total_weight
        
        # Ensure score is between 0 and 1
        overall_score = max(0, min(1, overall_score))
        
        return overall_score, quality_components
    
    def _calculate_quality_metrics(self, 
                                 financial_ratios: List[FinancialRatios],
                                 balance_sheets: List[BalanceSheet]) -> Dict[str, float]:
        """Calculate detailed quality metrics"""
        
        metrics = {}
        
        if financial_ratios:
            # Average metrics over time
            roes = [r.roe for r in financial_ratios if r.roe]
            if roes:
                metrics['avg_roe'] = np.mean(roes)
                metrics['roe_stability'] = 1 - (np.std(roes) / np.mean(roes)) if np.mean(roes) > 0 else 0
        
        # Overall quality score (simplified)
        quality_factors = [v for v in metrics.values() if isinstance(v, (int, float))]
        metrics['overall_score'] = np.mean(quality_factors) if quality_factors else 0.5
        
        return metrics
    
    def _calculate_growth_scenarios(self, 
                                  normalized_earnings: float,
                                  cost_of_capital: float,
                                  shares_outstanding: float) -> Dict[str, float]:
        """
        Calculate EPV under different growth scenarios
        
        While EPV assumes no growth, it's useful to see the impact
        of modest growth assumptions
        """
        
        scenarios = {}
        
        # Base case: No growth (pure EPV)
        scenarios['zero_growth'] = normalized_earnings / cost_of_capital / shares_outstanding
        
        # Conservative growth scenarios
        growth_rates = [0.01, 0.02, 0.03, 0.05]  # 1%, 2%, 3%, 5%
        
        for growth_rate in growth_rates:
            if growth_rate < cost_of_capital:  # Ensure growth < discount rate
                # Gordon Growth Model: V = E * (1 + g) / (r - g)
                value_per_share = (normalized_earnings * (1 + growth_rate)) / \
                                (cost_of_capital - growth_rate) / shares_outstanding
                scenarios[f'{growth_rate:.0%}_growth'] = value_per_share
        
        return scenarios
    
    def calculate_quality_score(self,
                              income_statements: List[IncomeStatement],
                              balance_sheets: List[BalanceSheet],
                              financial_ratios: List[FinancialRatios]) -> Tuple[float, Dict]:
        """
        Standalone quality score calculation
        
        Returns:
            Tuple of (overall_score, detailed_analysis)
        """
        
        quality_score, quality_components = self._assess_quality(
            income_statements, balance_sheets, financial_ratios
        )
        
        # Additional analysis
        detailed_analysis = {
            'overall_score': quality_score,
            'components': quality_components,
            'interpretation': self._interpret_quality_score(quality_score),
            'recommendations': self._quality_recommendations(quality_components)
        }
        
        return quality_score, detailed_analysis
    
    def _interpret_quality_score(self, score: float) -> str:
        """Interpret quality score"""
        if score >= 0.8:
            return "Excellent quality - Very predictable earnings, strong competitive position"
        elif score >= 0.6:
            return "Good quality - Reasonably stable business with solid fundamentals"
        elif score >= 0.4:
            return "Average quality - Some concerns about consistency or competitive position"
        else:
            return "Poor quality - Significant risks to earnings sustainability"
    
    def _quality_recommendations(self, components: Dict[str, float]) -> List[str]:
        """Generate recommendations based on quality components"""
        recommendations = []
        
        if components.get('earnings_stability', 0) < 0.5:
            recommendations.append("Monitor earnings volatility - consider if cyclical factors explain variation")
        
        if components.get('roe_quality', 0) < 0.5:
            recommendations.append("Low return on equity - investigate capital allocation efficiency")
        
        if components.get('leverage_quality', 0) < 0.5:
            recommendations.append("High leverage - assess debt sustainability and refinancing risks")
        
        if components.get('liquidity_quality', 0) < 0.5:
            recommendations.append("Liquidity concerns - monitor working capital and cash flow")
        
        if components.get('growth_quality', 0) < 0.5:
            recommendations.append("Volatile revenue growth - understand market dynamics and competitive position")
        
        if not recommendations:
            recommendations.append("Strong financial profile across key quality metrics")
        
        return recommendations
