"""
Research Report Generator
Creates comprehensive investment research reports with EPV analysis
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
import logging

from models.financial_models import (
    ResearchReport, EPVCalculation, CompanyProfile,
    IncomeStatement, BalanceSheet, CashFlowStatement,
    FinancialRatios, MarketData
)
from data.data_collector import DataCollector
from analysis.epv_calculator import EPVCalculator
from utils.cache_manager import CacheManager

class ResearchGenerator:
    """
    Generates comprehensive research reports combining:
    - Financial statement analysis
    - EPV calculations
    - Quality assessment
    - Peer comparisons
    - Risk analysis
    - Investment recommendations
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.data_collector = DataCollector(cache_manager)
        self.epv_calculator = EPVCalculator()
        self.logger = logging.getLogger(__name__)
    
    def generate_research_report(self, 
                               symbol: str, 
                               peer_symbols: Optional[List[str]] = None,
                               years_lookback: int = 10) -> ResearchReport:
        """
        Generate comprehensive research report for a company
        
        Args:
            symbol: Stock symbol to analyze
            peer_symbols: List of peer companies for comparison
            years_lookback: Years of historical data to analyze
            
        Returns:
            Complete ResearchReport object
        """
        
        self.logger.info(f"Generating research report for {symbol}")
        
        try:
            # Step 1: Collect comprehensive company data
            company_data = self.data_collector.collect_company_data(symbol, years_lookback)
            
            if not company_data['profile']:
                raise ValueError(f"Could not retrieve company profile for {symbol}")
            
            # Step 2: Calculate EPV
            current_price = self._get_current_price(company_data['market_data'])
            epv_calculation = self.epv_calculator.calculate_epv(
                symbol=symbol,
                income_statements=company_data['income_statements'],
                balance_sheets=company_data['balance_sheets'],
                cash_flow_statements=company_data['cash_flow_statements'],
                financial_ratios=company_data['financial_ratios'],
                current_price=current_price,
                company_profile=company_data['profile']
            )
            
            # Step 3: Quality assessment
            quality_score, quality_analysis = self.epv_calculator.calculate_quality_score(
                company_data['income_statements'],
                company_data['balance_sheets'],
                company_data['financial_ratios']
            )
            
            # Step 4: Peer comparison (if peers provided)
            peer_comparisons = {}
            if peer_symbols:
                peer_comparisons = self._generate_peer_comparisons(symbol, peer_symbols)
            
            # Step 5: Risk assessment
            risk_factors, risk_score = self._assess_risks(company_data, epv_calculation)
            
            # Step 6: Generate investment thesis and recommendation
            investment_thesis = self._generate_investment_thesis(
                company_data, epv_calculation, quality_analysis, peer_comparisons
            )
            recommendation, target_price = self._generate_recommendation(epv_calculation, quality_score, risk_score)
            
            # Step 7: Create comprehensive report
            report = ResearchReport(
                symbol=symbol,
                company_name=company_data['profile'].company_name,
                report_date=date.today(),
                profile=company_data['profile'],
                income_statements=company_data['income_statements'],
                balance_sheets=company_data['balance_sheets'],
                cash_flow_statements=company_data['cash_flow_statements'],
                financial_ratios=company_data['financial_ratios'],
                current_market_data=self._create_current_market_data(symbol, current_price),
                historical_prices=company_data['market_data'][-252:] if company_data['market_data'] else [],  # Last year
                epv_calculation=epv_calculation,
                quality_score=quality_score,
                quality_analysis=quality_analysis,
                peer_comparisons=peer_comparisons,
                risk_factors=risk_factors,
                risk_score=risk_score,
                investment_thesis=investment_thesis,
                recommendation=recommendation,
                target_price=target_price,
                confidence_level=self._calculate_confidence_level(quality_score, risk_score)
            )
            
            self.logger.info(f"Research report generated for {symbol}: {recommendation}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating research report for {symbol}: {e}")
            raise
    
    def _get_current_price(self, market_data: List[MarketData]) -> Optional[float]:
        """Get most recent stock price"""
        if market_data:
            latest_data = max(market_data, key=lambda x: x.date)
            return latest_data.price
        return None
    
    def _create_current_market_data(self, symbol: str, price: Optional[float]) -> Optional[MarketData]:
        """Create current market data snapshot"""
        if price:
            return MarketData(
                symbol=symbol,
                date=date.today(),
                price=price
            )
        return None
    
    def _generate_peer_comparisons(self, symbol: str, peer_symbols: List[str]) -> Dict:
        """Generate peer comparison analysis"""
        self.logger.info(f"Generating peer comparisons for {symbol}")
        
        comparisons = {
            'target_symbol': symbol,
            'peer_symbols': peer_symbols,
            'metrics_comparison': {},
            'epv_comparison': {},
            'quality_comparison': {},
            'summary': {}
        }
        
        try:
            # Get peer comparison data
            peer_data = self.data_collector.get_peer_comparison_data(symbol, peer_symbols)
            
            # Calculate metrics for each peer
            peer_metrics = {}
            for peer_symbol in peer_symbols:
                if peer_symbol in peer_data['peers']:
                    try:
                        peer_info = peer_data['peers'][peer_symbol]
                        
                        # Calculate EPV for peer
                        peer_epv = self.epv_calculator.calculate_epv(
                            symbol=peer_symbol,
                            income_statements=peer_info['income_statements'],
                            balance_sheets=peer_info['balance_sheets'],
                            cash_flow_statements=peer_info['cash_flow_statements'],
                            financial_ratios=peer_info['financial_ratios'],
                            company_profile=peer_info['profile']
                        )
                        
                        # Calculate quality score
                        peer_quality, _ = self.epv_calculator.calculate_quality_score(
                            peer_info['income_statements'],
                            peer_info['balance_sheets'],
                            peer_info['financial_ratios']
                        )
                        
                        peer_metrics[peer_symbol] = {
                            'epv_per_share': peer_epv.epv_per_share,
                            'quality_score': peer_quality,
                            'normalized_earnings': peer_epv.normalized_earnings,
                            'cost_of_capital': peer_epv.cost_of_capital
                        }
                        
                    except Exception as e:
                        self.logger.warning(f"Error analyzing peer {peer_symbol}: {e}")
            
            # Compile comparison metrics
            if peer_metrics:
                comparisons['epv_comparison'] = peer_metrics
                comparisons['summary'] = self._summarize_peer_comparison(symbol, peer_metrics)
            
        except Exception as e:
            self.logger.error(f"Error in peer comparison: {e}")
        
        return comparisons
    
    def _summarize_peer_comparison(self, symbol: str, peer_metrics: Dict) -> Dict:
        """Summarize peer comparison results"""
        if not peer_metrics:
            return {}
        
        epv_values = [metrics['epv_per_share'] for metrics in peer_metrics.values()]
        quality_scores = [metrics['quality_score'] for metrics in peer_metrics.values()]
        
        return {
            'peer_count': len(peer_metrics),
            'avg_peer_epv': np.mean(epv_values),
            'median_peer_epv': np.median(epv_values),
            'avg_peer_quality': np.mean(quality_scores),
            'peer_epv_range': (min(epv_values), max(epv_values)),
            'peer_quality_range': (min(quality_scores), max(quality_scores))
        }
    
    def _assess_risks(self, company_data: Dict, epv_calculation: EPVCalculation) -> Tuple[List[str], float]:
        """Assess investment risks and generate risk score"""
        risk_factors = []
        risk_score = 0.5  # Base risk (0 = low risk, 1 = high risk)
        
        try:
            # 1. Earnings volatility risk
            income_statements = company_data['income_statements']
            if income_statements and len(income_statements) >= 3:
                earnings = [stmt.net_income for stmt in income_statements if stmt.net_income]
                if earnings:
                    earnings_cv = np.std(earnings) / np.mean(earnings) if np.mean(earnings) > 0 else 1
                    if earnings_cv > 0.5:
                        risk_factors.append("High earnings volatility - unpredictable income stream")
                        risk_score += 0.15
                    elif earnings_cv > 0.3:
                        risk_factors.append("Moderate earnings volatility")
                        risk_score += 0.05
            
            # 2. Leverage risk
            balance_sheets = company_data['balance_sheets']
            if balance_sheets:
                latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
                if latest_bs.long_term_debt and latest_bs.total_equity:
                    debt_to_equity = latest_bs.long_term_debt / latest_bs.total_equity
                    if debt_to_equity > 1.0:
                        risk_factors.append("High leverage - significant debt burden")
                        risk_score += 0.2
                    elif debt_to_equity > 0.5:
                        risk_factors.append("Moderate leverage")
                        risk_score += 0.1
            
            # 3. Liquidity risk
            if balance_sheets:
                latest_bs = max(balance_sheets, key=lambda x: x.fiscal_year)
                if latest_bs.current_assets and latest_bs.current_liabilities:
                    current_ratio = latest_bs.current_assets / latest_bs.current_liabilities
                    if current_ratio < 1.0:
                        risk_factors.append("Liquidity concerns - current ratio below 1.0")
                        risk_score += 0.15
                    elif current_ratio < 1.5:
                        risk_factors.append("Tight liquidity position")
                        risk_score += 0.05
            
            # 4. Quality-based risks
            if epv_calculation.quality_score is not None:
                if epv_calculation.quality_score < 0.3:
                    risk_factors.append("Low quality business - earnings sustainability concerns")
                    risk_score += 0.2
                elif epv_calculation.quality_score < 0.5:
                    risk_factors.append("Below-average quality metrics")
                    risk_score += 0.1
            
            # 5. Market valuation risk
            if epv_calculation.margin_of_safety is not None:
                if epv_calculation.margin_of_safety < -50:  # Trading more than 50% above EPV
                    risk_factors.append("Significant overvaluation risk - trading well above intrinsic value")
                    risk_score += 0.15
                elif epv_calculation.margin_of_safety < -20:
                    risk_factors.append("Moderate overvaluation - limited margin of safety")
                    risk_score += 0.05
            
            # 6. Revenue concentration/growth risks
            if income_statements and len(income_statements) >= 3:
                revenues = [(stmt.fiscal_year, stmt.revenue) for stmt in income_statements 
                           if stmt.revenue and stmt.revenue > 0]
                revenues.sort(key=lambda x: x[0])
                
                if len(revenues) >= 3:
                    recent_growth = (revenues[-1][1] - revenues[-3][1]) / revenues[-3][1] / 2  # 2-year CAGR
                    if recent_growth < -0.05:  # Declining revenue
                        risk_factors.append("Revenue decline trend - market share or demand concerns")
                        risk_score += 0.15
            
            # Cap risk score at 1.0
            risk_score = min(1.0, risk_score)
            
            # If no specific risks identified, add default factors
            if not risk_factors:
                risk_factors.append("General market and economic risks")
                risk_factors.append("Industry competition and disruption risks")
                risk_factors.append("Management and corporate governance risks")
            
        except Exception as e:
            self.logger.error(f"Error in risk assessment: {e}")
            risk_factors.append("Risk assessment incomplete due to data limitations")
            risk_score = 0.6  # Conservative default
        
        return risk_factors, risk_score
    
    def _generate_investment_thesis(self, 
                                  company_data: Dict, 
                                  epv_calculation: EPVCalculation,
                                  quality_analysis: Dict,
                                  peer_comparisons: Dict) -> str:
        """Generate investment thesis narrative"""
        
        profile = company_data['profile']
        thesis_parts = []
        
        # Company overview
        thesis_parts.append(f"{profile.company_name} ({epv_calculation.symbol}) operates in the {profile.sector or 'N/A'} sector")
        
        if profile.description:
            # Truncate description if too long
            desc = profile.description[:200] + "..." if len(profile.description) > 200 else profile.description
            thesis_parts.append(f"Business: {desc}")
        
        # EPV analysis
        if epv_calculation.current_price:
            thesis_parts.append(f"Current price: ${epv_calculation.current_price:.2f}")
            thesis_parts.append(f"EPV per share: ${epv_calculation.epv_per_share:.2f}")
            
            if epv_calculation.margin_of_safety is not None:
                if epv_calculation.margin_of_safety > 20:
                    thesis_parts.append(f"Trading at significant discount to EPV ({epv_calculation.margin_of_safety:.1f}% margin of safety)")
                elif epv_calculation.margin_of_safety > 0:
                    thesis_parts.append(f"Trading below EPV with {epv_calculation.margin_of_safety:.1f}% margin of safety")
                else:
                    thesis_parts.append(f"Trading above EPV by {abs(epv_calculation.margin_of_safety):.1f}%")
        
        # Quality assessment
        quality_interp = quality_analysis.get('interpretation', '')
        if quality_interp:
            thesis_parts.append(f"Quality: {quality_interp}")
        
        # Key strengths and concerns
        recommendations = quality_analysis.get('recommendations', [])
        if recommendations:
            positive_recs = [rec for rec in recommendations if 'strong' in rec.lower() or 'good' in rec.lower()]
            concern_recs = [rec for rec in recommendations if any(word in rec.lower() for word in ['monitor', 'concern', 'low', 'high leverage'])]
            
            if positive_recs:
                thesis_parts.append(f"Strengths: {'; '.join(positive_recs)}")
            if concern_recs:
                thesis_parts.append(f"Key considerations: {'; '.join(concern_recs)}")
        
        # Peer comparison insights
        if peer_comparisons and 'summary' in peer_comparisons:
            summary = peer_comparisons['summary']
            if summary:
                avg_peer_epv = summary.get('avg_peer_epv')
                if avg_peer_epv and epv_calculation.epv_per_share:
                    if epv_calculation.epv_per_share > avg_peer_epv * 1.1:
                        thesis_parts.append(f"EPV exceeds peer average by {((epv_calculation.epv_per_share / avg_peer_epv - 1) * 100):.1f}%")
                    elif epv_calculation.epv_per_share < avg_peer_epv * 0.9:
                        thesis_parts.append(f"EPV below peer average by {((1 - epv_calculation.epv_per_share / avg_peer_epv) * 100):.1f}%")
        
        return ". ".join(thesis_parts) + "."
    
    def _generate_recommendation(self, 
                               epv_calculation: EPVCalculation, 
                               quality_score: float, 
                               risk_score: float) -> Tuple[str, Optional[float]]:
        """Generate investment recommendation and target price"""
        
        # Decision matrix based on margin of safety, quality, and risk
        margin_of_safety = epv_calculation.margin_of_safety or 0
        
        # Calculate target price (EPV adjusted for quality)
        quality_adjustment = 1.0
        if quality_score >= 0.8:
            quality_adjustment = 1.1  # 10% premium for high quality
        elif quality_score >= 0.6:
            quality_adjustment = 1.0   # No adjustment for good quality
        elif quality_score >= 0.4:
            quality_adjustment = 0.95  # 5% discount for average quality
        else:
            quality_adjustment = 0.85  # 15% discount for poor quality
        
        target_price = epv_calculation.epv_per_share * quality_adjustment
        
        # Generate recommendation
        if margin_of_safety >= 25 and quality_score >= 0.6 and risk_score <= 0.6:
            recommendation = "STRONG BUY"
        elif margin_of_safety >= 15 and quality_score >= 0.5 and risk_score <= 0.7:
            recommendation = "BUY"
        elif margin_of_safety >= 5 and quality_score >= 0.4 and risk_score <= 0.8:
            recommendation = "WEAK BUY"
        elif margin_of_safety >= -10 and quality_score >= 0.4:
            recommendation = "HOLD"
        elif margin_of_safety >= -25:
            recommendation = "WEAK SELL"
        else:
            recommendation = "SELL"
        
        # Adjust for high risk
        if risk_score > 0.8:
            if recommendation in ["STRONG BUY", "BUY"]:
                recommendation = "HOLD"
            elif recommendation in ["WEAK BUY", "HOLD"]:
                recommendation = "WEAK SELL"
        
        return recommendation, target_price
    
    def _calculate_confidence_level(self, quality_score: float, risk_score: float) -> float:
        """Calculate confidence level in the analysis"""
        
        # Base confidence from data quality
        base_confidence = 0.7
        
        # Adjust for quality score
        quality_adjustment = (quality_score - 0.5) * 0.3  # +/- 15% based on quality
        
        # Adjust for risk score (higher risk = lower confidence)
        risk_adjustment = -(risk_score - 0.5) * 0.2  # +/- 10% based on risk
        
        confidence = base_confidence + quality_adjustment + risk_adjustment
        
        # Cap between 0.3 and 0.95
        return max(0.3, min(0.95, confidence))
    
    def export_report(self, report: ResearchReport, format: str = "json") -> str:
        """Export research report to specified format"""
        
        if format.lower() == "json":
            return self._export_json(report)
        elif format.lower() == "csv":
            return self._export_csv(report)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, report: ResearchReport) -> str:
        """Export report as JSON"""
        import json
        from dataclasses import asdict
        
        # Convert dataclasses to dict, handling datetime objects
        def serialize_datetime(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError(f"Object {obj} is not JSON serializable")
        
        report_dict = asdict(report)
        return json.dumps(report_dict, indent=2, default=serialize_datetime)
    
    def _export_csv(self, report: ResearchReport) -> str:
        """Export key metrics as CSV"""
        
        # Create summary metrics DataFrame
        data = {
            'Symbol': [report.symbol],
            'Company': [report.company_name],
            'EPV_Per_Share': [report.epv_calculation.epv_per_share if report.epv_calculation else None],
            'Current_Price': [report.epv_calculation.current_price if report.epv_calculation else None],
            'Margin_of_Safety': [report.epv_calculation.margin_of_safety if report.epv_calculation else None],
            'Quality_Score': [report.quality_score],
            'Risk_Score': [report.risk_score],
            'Recommendation': [report.recommendation],
            'Target_Price': [report.target_price],
            'Confidence_Level': [report.confidence_level]
        }
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False)
