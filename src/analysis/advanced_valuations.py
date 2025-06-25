"""
Advanced Valuation Models
Implements DCF, Asset-based, and Market multiples valuation alongside EPV
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
from datetime import date, datetime
import logging
from dataclasses import dataclass, field
from scipy import stats

from models.financial_models import (
    IncomeStatement, BalanceSheet, CashFlowStatement, 
    FinancialRatios, CompanyProfile
)
from config.config import config

@dataclass
class DCFCalculation:
    """Discounted Cash Flow calculation results"""
    symbol: str
    calculation_date: date
    
    # Projections
    projection_years: int
    revenue_projections: List[float]
    fcf_projections: List[float]
    
    # Assumptions
    terminal_growth_rate: float
    discount_rate: float
    
    # Results
    present_value_fcf: float
    terminal_value: float
    enterprise_value: float
    equity_value: float
    dcf_per_share: float
    
    # Sensitivity analysis
    sensitivity_analysis: Dict[str, Dict[str, float]] = field(default_factory=dict)

@dataclass
class AssetBasedValuation:
    """Asset-based valuation results"""
    symbol: str
    calculation_date: date
    
    # Book value analysis
    book_value_per_share: float
    tangible_book_value_per_share: float
    
    # Asset adjustments
    asset_adjustments: Dict[str, float] = field(default_factory=dict)
    liability_adjustments: Dict[str, float] = field(default_factory=dict)
    
    # Results
    adjusted_book_value: float
    liquidation_value: float
    replacement_cost: float
    
    # Per share values
    adjusted_book_value_per_share: float
    liquidation_value_per_share: float

@dataclass
class MarketMultiplesValuation:
    """Market multiples valuation results"""
    symbol: str
    calculation_date: date
    
    # Company metrics
    trailing_pe: Optional[float]
    forward_pe: Optional[float]
    price_to_book: Optional[float]
    price_to_sales: Optional[float]
    ev_to_ebitda: Optional[float]
    
    # Peer comparisons
    peer_multiples: Dict[str, Dict[str, float]] = field(default_factory=dict)
    industry_multiples: Dict[str, float] = field(default_factory=dict)
    
    # Valuation estimates
    pe_based_value: Optional[float]
    pb_based_value: Optional[float]
    ps_based_value: Optional[float]
    ev_ebitda_based_value: Optional[float]
    
    # Summary
    multiples_average_value: float
    multiples_median_value: float

@dataclass
class MonteCarloResults:
    """Monte Carlo simulation results"""
    symbol: str
    simulation_date: date
    
    # Simulation parameters
    num_simulations: int
    confidence_intervals: List[float]  # e.g., [0.05, 0.25, 0.75, 0.95]
    
    # Results distribution
    value_distribution: List[float]
    mean_value: float
    median_value: float
    std_deviation: float
    
    # Risk metrics
    value_at_risk: Dict[float, float]  # VaR at different confidence levels
    probability_of_loss: float
    upside_potential: float

class AdvancedValuationEngine:
    """
    Advanced valuation engine implementing multiple valuation methodologies
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def calculate_dcf_valuation(self, 
                               symbol: str,
                               income_statements: List[IncomeStatement],
                               balance_sheets: List[BalanceSheet],
                               cash_flow_statements: List[CashFlowStatement],
                               projection_years: int = 5,
                               terminal_growth_rate: float = 0.025,
                               discount_rate: Optional[float] = None) -> DCFCalculation:
        """
        Calculate Discounted Cash Flow valuation
        
        Args:
            symbol: Stock symbol
            income_statements: Historical income statements
            balance_sheets: Historical balance sheets
            cash_flow_statements: Historical cash flow statements
            projection_years: Number of years to project
            terminal_growth_rate: Terminal growth rate assumption
            discount_rate: Discount rate (WACC), if None will estimate
            
        Returns:
            DCFCalculation object with detailed results
        """
        
        self.logger.info(f"Calculating DCF valuation for {symbol}")
        
        try:
            # Estimate discount rate if not provided
            if discount_rate is None:
                discount_rate = self._estimate_discount_rate(balance_sheets, income_statements)
            
            # Project revenues
            revenue_projections = self._project_revenues(income_statements, projection_years)
            
            # Project free cash flows
            fcf_projections = self._project_free_cash_flows(
                income_statements, cash_flow_statements, revenue_projections
            )
            
            # Calculate present value of projected FCFs
            present_value_fcf = sum(
                fcf / (1 + discount_rate) ** (i + 1) 
                for i, fcf in enumerate(fcf_projections)
            )
            
            # Calculate terminal value
            terminal_fcf = fcf_projections[-1] * (1 + terminal_growth_rate)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
            terminal_pv = terminal_value / (1 + discount_rate) ** projection_years
            
            # Calculate enterprise and equity value
            enterprise_value = present_value_fcf + terminal_pv
            
            # Adjust for net cash/debt
            latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
            net_cash = 0
            if latest_bs.cash_and_equivalents and latest_bs.long_term_debt:
                net_cash = latest_bs.cash_and_equivalents - latest_bs.long_term_debt
            
            equity_value = enterprise_value + net_cash
            
            # Calculate per share value
            shares_outstanding = self._get_shares_outstanding(income_statements)
            dcf_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            
            # Perform sensitivity analysis
            sensitivity_analysis = self._dcf_sensitivity_analysis(
                fcf_projections, terminal_fcf, shares_outstanding,
                base_discount_rate=discount_rate,
                base_terminal_growth=terminal_growth_rate,
                net_cash=net_cash
            )
            
            return DCFCalculation(
                symbol=symbol,
                calculation_date=date.today(),
                projection_years=projection_years,
                revenue_projections=revenue_projections,
                fcf_projections=fcf_projections,
                terminal_growth_rate=terminal_growth_rate,
                discount_rate=discount_rate,
                present_value_fcf=present_value_fcf,
                terminal_value=terminal_pv,
                enterprise_value=enterprise_value,
                equity_value=equity_value,
                dcf_per_share=dcf_per_share,
                sensitivity_analysis=sensitivity_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating DCF for {symbol}: {e}")
            raise
    
    def calculate_asset_based_valuation(self,
                                      symbol: str,
                                      balance_sheets: List[BalanceSheet],
                                      income_statements: List[IncomeStatement]) -> AssetBasedValuation:
        """Calculate asset-based valuation"""
        
        self.logger.info(f"Calculating asset-based valuation for {symbol}")
        
        try:
            latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
            shares_outstanding = self._get_shares_outstanding(income_statements)
            
            # Book value calculations
            book_value_per_share = (latest_bs.total_equity / shares_outstanding 
                                  if latest_bs.total_equity and shares_outstanding > 0 else 0)
            
            # Estimate intangible assets (rough approximation)
            intangible_assets = 0
            if latest_bs.total_assets and latest_bs.total_equity:
                # Assume intangibles are assets not easily valued
                intangible_assets = max(0, latest_bs.total_assets * 0.1)  # Conservative estimate
            
            tangible_book_value = latest_bs.total_equity - intangible_assets
            tangible_book_value_per_share = (tangible_book_value / shares_outstanding 
                                           if shares_outstanding > 0 else 0)
            
            # Asset adjustments
            asset_adjustments = self._calculate_asset_adjustments(latest_bs)
            liability_adjustments = self._calculate_liability_adjustments(latest_bs)
            
            # Calculate adjusted values
            total_asset_adjustments = sum(asset_adjustments.values())
            total_liability_adjustments = sum(liability_adjustments.values())
            
            adjusted_book_value = latest_bs.total_equity + total_asset_adjustments - total_liability_adjustments
            adjusted_book_value_per_share = (adjusted_book_value / shares_outstanding 
                                           if shares_outstanding > 0 else 0)
            
            # Liquidation value (conservative estimate)
            liquidation_value = adjusted_book_value * 0.7  # Assume 30% discount in liquidation
            liquidation_value_per_share = (liquidation_value / shares_outstanding 
                                         if shares_outstanding > 0 else 0)
            
            return AssetBasedValuation(
                symbol=symbol,
                calculation_date=date.today(),
                book_value_per_share=book_value_per_share,
                tangible_book_value_per_share=tangible_book_value_per_share,
                asset_adjustments=asset_adjustments,
                liability_adjustments=liability_adjustments,
                adjusted_book_value=adjusted_book_value,
                liquidation_value=liquidation_value,
                replacement_cost=adjusted_book_value * 1.2,  # Estimate replacement cost
                adjusted_book_value_per_share=adjusted_book_value_per_share,
                liquidation_value_per_share=liquidation_value_per_share
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating asset-based valuation for {symbol}: {e}")
            raise
    
    def calculate_market_multiples_valuation(self,
                                           symbol: str,
                                           income_statements: List[IncomeStatement],
                                           balance_sheets: List[BalanceSheet],
                                           current_price: Optional[float] = None,
                                           peer_data: Optional[Dict] = None) -> MarketMultiplesValuation:
        """Calculate market multiples valuation"""
        
        self.logger.info(f"Calculating market multiples valuation for {symbol}")
        
        try:
            latest_income = max(income_statements, key=lambda x: x.fiscal_year)
            latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
            shares_outstanding = self._get_shares_outstanding(income_statements)
            
            # Calculate current multiples
            market_cap = current_price * shares_outstanding if current_price and shares_outstanding > 0 else None
            
            trailing_pe = None
            if current_price and latest_income.eps and latest_income.eps > 0:
                trailing_pe = current_price / latest_income.eps
            
            price_to_book = None
            if current_price and latest_bs.total_equity and shares_outstanding > 0:
                book_value_per_share = latest_bs.total_equity / shares_outstanding
                if book_value_per_share > 0:
                    price_to_book = current_price / book_value_per_share
            
            price_to_sales = None
            if market_cap and latest_income.revenue and latest_income.revenue > 0:
                price_to_sales = market_cap / latest_income.revenue
            
            # Industry multiples (approximate values - would need industry data)
            industry_multiples = self._get_industry_multiples(symbol)
            
            # Calculate valuation estimates based on multiples
            valuations = {}
            
            if latest_income.eps and latest_income.eps > 0:
                pe_based_value = latest_income.eps * industry_multiples.get('pe', 15.0)
                valuations['pe_based_value'] = pe_based_value
            
            if latest_bs.total_equity and shares_outstanding > 0:
                book_value_per_share = latest_bs.total_equity / shares_outstanding
                pb_based_value = book_value_per_share * industry_multiples.get('pb', 2.0)
                valuations['pb_based_value'] = pb_based_value
            
            if latest_income.revenue and shares_outstanding > 0:
                revenue_per_share = latest_income.revenue / shares_outstanding
                ps_based_value = revenue_per_share * industry_multiples.get('ps', 3.0)
                valuations['ps_based_value'] = ps_based_value
            
            # Calculate average and median
            value_list = list(valuations.values())
            multiples_average_value = np.mean(value_list) if value_list else 0
            multiples_median_value = np.median(value_list) if value_list else 0
            
            return MarketMultiplesValuation(
                symbol=symbol,
                calculation_date=date.today(),
                trailing_pe=trailing_pe,
                forward_pe=None,  # Would need forward estimates
                price_to_book=price_to_book,
                price_to_sales=price_to_sales,
                ev_to_ebitda=None,  # Would need EBITDA calculation
                peer_multiples=peer_data or {},
                industry_multiples=industry_multiples,
                pe_based_value=valuations.get('pe_based_value'),
                pb_based_value=valuations.get('pb_based_value'),
                ps_based_value=valuations.get('ps_based_value'),
                ev_ebitda_based_value=None,
                multiples_average_value=multiples_average_value,
                multiples_median_value=multiples_median_value
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating market multiples valuation for {symbol}: {e}")
            raise
    
    def run_monte_carlo_simulation(self,
                                 symbol: str,
                                 base_valuation: float,
                                 volatility_assumptions: Dict[str, float],
                                 num_simulations: int = 10000) -> MonteCarloResults:
        """
        Run Monte Carlo simulation for valuation uncertainty
        
        Args:
            symbol: Stock symbol
            base_valuation: Base case valuation
            volatility_assumptions: Dict of parameter volatilities
            num_simulations: Number of simulations to run
            
        Returns:
            MonteCarloResults with simulation outcomes
        """
        
        self.logger.info(f"Running Monte Carlo simulation for {symbol}")
        
        try:
            # Define parameter distributions
            revenue_growth_vol = volatility_assumptions.get('revenue_growth', 0.05)
            margin_vol = volatility_assumptions.get('margin', 0.02)
            multiple_vol = volatility_assumptions.get('multiple', 0.15)
            
            # Run simulations
            simulation_results = []
            
            for _ in range(num_simulations):
                # Sample from distributions
                revenue_shock = np.random.normal(0, revenue_growth_vol)
                margin_shock = np.random.normal(0, margin_vol)
                multiple_shock = np.random.normal(0, multiple_vol)
                
                # Calculate scenario valuation
                combined_shock = 1 + revenue_shock + margin_shock + multiple_shock
                scenario_value = base_valuation * combined_shock
                simulation_results.append(scenario_value)
            
            # Calculate statistics
            simulation_results = np.array(simulation_results)
            mean_value = np.mean(simulation_results)
            median_value = np.median(simulation_results)
            std_deviation = np.std(simulation_results)
            
            # Calculate Value at Risk
            confidence_intervals = [0.05, 0.25, 0.75, 0.95]
            value_at_risk = {}
            for ci in confidence_intervals:
                value_at_risk[ci] = np.percentile(simulation_results, ci * 100)
            
            # Risk metrics
            probability_of_loss = np.mean(simulation_results < base_valuation * 0.8)  # 20% loss threshold
            upside_potential = np.mean(simulation_results > base_valuation * 1.2)  # 20% gain threshold
            
            return MonteCarloResults(
                symbol=symbol,
                simulation_date=date.today(),
                num_simulations=num_simulations,
                confidence_intervals=confidence_intervals,
                value_distribution=simulation_results.tolist(),
                mean_value=mean_value,
                median_value=median_value,
                std_deviation=std_deviation,
                value_at_risk=value_at_risk,
                probability_of_loss=probability_of_loss,
                upside_potential=upside_potential
            )
            
        except Exception as e:
            self.logger.error(f"Error running Monte Carlo simulation for {symbol}: {e}")
            raise
    
    def _project_revenues(self, income_statements: List[IncomeStatement], years: int) -> List[float]:
        """Project future revenues based on historical growth"""
        
        # Get historical revenues
        revenues = [(stmt.fiscal_year, stmt.revenue) for stmt in income_statements 
                   if stmt.revenue and stmt.revenue > 0]
        revenues.sort(key=lambda x: x[0])
        
        if len(revenues) < 3:
            raise ValueError("Insufficient revenue history for projection")
        
        # Calculate historical growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            growth = (revenues[i][1] - revenues[i-1][1]) / revenues[i-1][1]
            growth_rates.append(growth)
        
        # Estimate future growth (conservative approach)
        recent_growth = np.mean(growth_rates[-3:]) if len(growth_rates) >= 3 else np.mean(growth_rates)
        long_term_growth = np.mean(growth_rates)
        
        # Gradually decline growth rate to long-term sustainable level
        base_revenue = revenues[-1][1]
        projections = []
        
        for year in range(years):
            # Declining growth rate approach
            growth_rate = recent_growth * (0.8 ** year) + long_term_growth * (1 - 0.8 ** year)
            growth_rate = max(growth_rate, 0.02)  # Minimum 2% growth
            growth_rate = min(growth_rate, 0.15)  # Maximum 15% growth
            
            if year == 0:
                projected_revenue = base_revenue * (1 + growth_rate)
            else:
                projected_revenue = projections[-1] * (1 + growth_rate)
            
            projections.append(projected_revenue)
        
        return projections
    
    def _project_free_cash_flows(self, 
                                income_statements: List[IncomeStatement],
                                cash_flow_statements: List[CashFlowStatement],
                                revenue_projections: List[float]) -> List[float]:
        """Project future free cash flows"""
        
        # Calculate historical FCF margins
        fcf_margins = []
        for cf_stmt in cash_flow_statements:
            if cf_stmt.free_cash_flow:
                # Find matching income statement
                matching_income = next(
                    (stmt for stmt in income_statements if stmt.fiscal_year == cf_stmt.fiscal_year),
                    None
                )
                if matching_income and matching_income.revenue and matching_income.revenue > 0:
                    margin = cf_stmt.free_cash_flow / matching_income.revenue
                    fcf_margins.append(margin)
        
        if not fcf_margins:
            # Estimate FCF margin from net income margin
            net_margins = []
            for stmt in income_statements:
                if stmt.revenue and stmt.net_income and stmt.revenue > 0:
                    margin = stmt.net_income / stmt.revenue
                    net_margins.append(margin)
            
            avg_net_margin = np.mean(net_margins) if net_margins else 0.1
            estimated_fcf_margin = avg_net_margin * 0.8  # Conservative estimate
            fcf_margins = [estimated_fcf_margin]
        
        # Use conservative FCF margin
        avg_fcf_margin = np.mean(fcf_margins)
        conservative_fcf_margin = avg_fcf_margin * 0.9  # 10% conservatism factor
        
        # Project FCFs
        fcf_projections = []
        for revenue in revenue_projections:
            fcf = revenue * conservative_fcf_margin
            fcf_projections.append(fcf)
        
        return fcf_projections
    
    def _estimate_discount_rate(self, 
                              balance_sheets: List[BalanceSheet],
                              income_statements: List[IncomeStatement]) -> float:
        """Estimate appropriate discount rate (WACC)"""
        
        # Base risk-free rate + equity risk premium
        base_rate = config.analysis.risk_free_rate + config.analysis.market_risk_premium
        
        # Adjust for company-specific risk
        latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
        
        # Size adjustment (smaller companies get higher discount rate)
        if latest_bs.total_assets:
            if latest_bs.total_assets < 1e9:  # < $1B assets
                size_adjustment = 0.02
            elif latest_bs.total_assets < 10e9:  # < $10B assets
                size_adjustment = 0.01
            else:
                size_adjustment = 0
        else:
            size_adjustment = 0.02
        
        # Leverage adjustment
        leverage_adjustment = 0
        if latest_bs.long_term_debt and latest_bs.total_equity:
            debt_to_equity = latest_bs.long_term_debt / latest_bs.total_equity
            if debt_to_equity > 1.0:
                leverage_adjustment = 0.01
            elif debt_to_equity > 0.5:
                leverage_adjustment = 0.005
        
        discount_rate = base_rate + size_adjustment + leverage_adjustment
        return max(discount_rate, 0.08)  # Minimum 8%
    
    def _get_shares_outstanding(self, income_statements: List[IncomeStatement]) -> float:
        """Get shares outstanding from most recent data"""
        
        for stmt in sorted(income_statements, key=lambda x: x.fiscal_year, reverse=True):
            if stmt.shares_outstanding:
                return stmt.shares_outstanding
        
        # Estimate from EPS and net income
        for stmt in sorted(income_statements, key=lambda x: x.fiscal_year, reverse=True):
            if stmt.eps and stmt.net_income and stmt.eps != 0:
                return stmt.net_income / stmt.eps
        
        return 1000000  # Default fallback
    
    def _dcf_sensitivity_analysis(self, 
                                fcf_projections: List[float],
                                terminal_fcf: float,
                                shares_outstanding: float,
                                base_discount_rate: float,
                                base_terminal_growth: float,
                                net_cash: float) -> Dict[str, Dict[str, float]]:
        """Perform sensitivity analysis on DCF inputs"""
        
        sensitivity = {}
        
        # Discount rate sensitivity
        discount_rates = [base_discount_rate - 0.01, base_discount_rate, base_discount_rate + 0.01]
        growth_rates = [base_terminal_growth - 0.005, base_terminal_growth, base_terminal_growth + 0.005]
        
        sensitivity['discount_rate_sensitivity'] = {}
        sensitivity['terminal_growth_sensitivity'] = {}
        sensitivity['combined_sensitivity'] = {}
        
        for dr in discount_rates:
            pv_fcf = sum(fcf / (1 + dr) ** (i + 1) for i, fcf in enumerate(fcf_projections))
            terminal_value = terminal_fcf / (dr - base_terminal_growth) / (1 + dr) ** len(fcf_projections)
            equity_value = pv_fcf + terminal_value + net_cash
            per_share_value = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            sensitivity['discount_rate_sensitivity'][f'{dr:.1%}'] = per_share_value
        
        for gr in growth_rates:
            if gr < base_discount_rate:  # Ensure growth < discount rate
                pv_fcf = sum(fcf / (1 + base_discount_rate) ** (i + 1) for i, fcf in enumerate(fcf_projections))
                terminal_value = terminal_fcf / (base_discount_rate - gr) / (1 + base_discount_rate) ** len(fcf_projections)
                equity_value = pv_fcf + terminal_value + net_cash
                per_share_value = equity_value / shares_outstanding if shares_outstanding > 0 else 0
                sensitivity['terminal_growth_sensitivity'][f'{gr:.1%}'] = per_share_value
        
        return sensitivity
    
    def _calculate_asset_adjustments(self, balance_sheet: BalanceSheet) -> Dict[str, float]:
        """Calculate adjustments to asset values"""
        
        adjustments = {}
        
        # Inventory adjustment (assume some obsolescence)
        if balance_sheet.inventory:
            adjustments['inventory_markdown'] = -balance_sheet.inventory * 0.1
        
        # Receivables adjustment (assume some bad debt)
        if balance_sheet.receivables:
            adjustments['receivables_provision'] = -balance_sheet.receivables * 0.05
        
        return adjustments
    
    def _calculate_liability_adjustments(self, balance_sheet: BalanceSheet) -> Dict[str, float]:
        """Calculate adjustments to liability values"""
        
        adjustments = {}
        
        # Off-balance sheet obligations (estimated)
        if balance_sheet.total_assets:
            adjustments['off_balance_sheet_estimate'] = balance_sheet.total_assets * 0.02
        
        return adjustments
    
    def _get_industry_multiples(self, symbol: str) -> Dict[str, float]:
        """Get industry average multiples (mock data - would need real industry data)"""
        
        # Industry multiples by sector (approximate values)
        industry_multiples = {
            'Technology': {'pe': 25.0, 'pb': 4.0, 'ps': 6.0, 'ev_ebitda': 18.0},
            'Healthcare': {'pe': 18.0, 'pb': 3.0, 'ps': 4.0, 'ev_ebitda': 14.0},
            'Financial': {'pe': 12.0, 'pb': 1.2, 'ps': 2.5, 'ev_ebitda': 10.0},
            'Consumer': {'pe': 20.0, 'pb': 2.5, 'ps': 1.8, 'ev_ebitda': 12.0},
            'Industrial': {'pe': 16.0, 'pb': 2.0, 'ps': 1.5, 'ev_ebitda': 11.0},
            'Energy': {'pe': 14.0, 'pb': 1.5, 'ps': 1.2, 'ev_ebitda': 8.0},
            'Materials': {'pe': 15.0, 'pb': 1.8, 'ps': 1.3, 'ev_ebitda': 9.0},
            'Utilities': {'pe': 18.0, 'pb': 1.4, 'ps': 2.0, 'ev_ebitda': 10.0},
            'Default': {'pe': 18.0, 'pb': 2.5, 'ps': 3.0, 'ev_ebitda': 12.0}
        }
        
        # Would need to determine sector from symbol or company data
        # For now, return default multiples
        return industry_multiples['Default']
