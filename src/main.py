"""
Main EPV Research Platform Application
Entry point for the earnings power value research and analysis system
"""
import sys
import logging
from pathlib import Path
from typing import List, Optional
import argparse

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from data.data_collector import DataCollector
from data.alternative_data import AlternativeDataCollector
from analysis.epv_calculator import EPVCalculator
from analysis.research_generator import ResearchGenerator
from analysis.advanced_valuations import AdvancedValuationEngine
from analysis.portfolio_manager import PortfolioManager
from analysis.report_generator import ProfessionalReportGenerator, ComplianceInfo
from utils.cache_manager import CacheManager
from config.config import config, setup_directories

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

class EPVResearchPlatform:
    """
    Main application class for the EPV Research Platform
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.data_collector = DataCollector(self.cache_manager)
        self.epv_calculator = EPVCalculator()
        self.research_generator = ResearchGenerator(self.cache_manager)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("EPV Research Platform initialized")
    
    def analyze_stock(self, 
                     symbol: str, 
                     peer_symbols: Optional[List[str]] = None,
                     years: int = 10,
                     export_format: Optional[str] = None) -> dict:
        """
        Perform comprehensive analysis of a stock
        
        Args:
            symbol: Stock symbol to analyze
            peer_symbols: Optional list of peer companies
            years: Years of historical data to analyze
            export_format: Export format (json, csv, or None)
            
        Returns:
            Dictionary with analysis results
        """
        
        try:
            self.logger.info(f"Starting analysis for {symbol}")
            
            # Generate comprehensive research report
            report = self.research_generator.generate_research_report(
                symbol=symbol,
                peer_symbols=peer_symbols,
                years_lookback=years
            )
            
            # Create summary results
            results = {
                'symbol': report.symbol,
                'company_name': report.company_name,
                'analysis_date': report.report_date.isoformat(),
                'epv_per_share': report.epv_calculation.epv_per_share if report.epv_calculation else None,
                'current_price': report.epv_calculation.current_price if report.epv_calculation else None,
                'margin_of_safety': report.epv_calculation.margin_of_safety if report.epv_calculation else None,
                'quality_score': report.quality_score,
                'risk_score': report.risk_score,
                'recommendation': report.recommendation,
                'target_price': report.target_price,
                'confidence_level': report.confidence_level,
                'investment_thesis': report.investment_thesis,
                'risk_factors': report.risk_factors,
                'peer_comparison': report.peer_comparisons,
                'full_report': report
            }
            
            # Export if requested
            if export_format:
                export_data = self.research_generator.export_report(report, export_format)
                export_filename = f"{symbol}_analysis_{report.report_date.strftime('%Y%m%d')}.{export_format}"
                
                with open(f"exports/{export_filename}", 'w') as f:
                    f.write(export_data)
                
                results['export_file'] = export_filename
                self.logger.info(f"Analysis exported to {export_filename}")
            
            self.logger.info(f"Analysis complete for {symbol}: {report.recommendation}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            raise
    
    def quick_epv(self, symbol: str) -> dict:
        """
        Quick EPV calculation without full research report
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary with EPV results
        """
        
        try:
            self.logger.info(f"Quick EPV calculation for {symbol}")
            
            # Collect basic data
            company_data = self.data_collector.collect_company_data(symbol, years=5)
            
            # Calculate EPV
            current_price = None
            if company_data['market_data']:
                latest_data = max(company_data['market_data'], key=lambda x: x.date)
                current_price = latest_data.price
            
            epv_calculation = self.epv_calculator.calculate_epv(
                symbol=symbol,
                income_statements=company_data['income_statements'],
                balance_sheets=company_data['balance_sheets'],
                cash_flow_statements=company_data['cash_flow_statements'],
                financial_ratios=company_data['financial_ratios'],
                current_price=current_price
            )
            
            # Return key metrics
            return {
                'symbol': symbol,
                'company_name': company_data['profile'].company_name if company_data['profile'] else symbol,
                'epv_per_share': epv_calculation.epv_per_share,
                'current_price': epv_calculation.current_price,
                'margin_of_safety': epv_calculation.margin_of_safety,
                'quality_score': epv_calculation.quality_score,
                'normalized_earnings': epv_calculation.normalized_earnings,
                'cost_of_capital': epv_calculation.cost_of_capital,
                'growth_scenarios': epv_calculation.growth_scenarios
            }
            
        except Exception as e:
            self.logger.error(f"Error in quick EPV for {symbol}: {e}")
            raise
    
    def batch_analysis(self, symbols: List[str], export_summary: bool = True) -> dict:
        """
        Perform batch analysis on multiple stocks
        
        Args:
            symbols: List of stock symbols to analyze
            export_summary: Whether to export summary results
            
        Returns:
            Dictionary with batch results
        """
        
        results = {
            'batch_date': config.analysis.earnings_lookback_years,
            'symbols_analyzed': [],
            'successful_analyses': 0,
            'failed_analyses': 0,
            'results': {},
            'summary_stats': {}
        }
        
        self.logger.info(f"Starting batch analysis for {len(symbols)} symbols")
        
        for symbol in symbols:
            try:
                quick_results = self.quick_epv(symbol)
                results['results'][symbol] = quick_results
                results['symbols_analyzed'].append(symbol)
                results['successful_analyses'] += 1
                
                self.logger.info(f"✓ {symbol}: EPV=${quick_results['epv_per_share']:.2f}, "
                               f"Quality={quick_results['quality_score']:.2f}")
                
            except Exception as e:
                self.logger.error(f"✗ {symbol}: {e}")
                results['failed_analyses'] += 1
                results['results'][symbol] = {'error': str(e)}
        
        # Calculate summary statistics
        successful_results = [r for r in results['results'].values() if 'error' not in r]
        if successful_results:
            epv_values = [r['epv_per_share'] for r in successful_results if r['epv_per_share']]
            quality_scores = [r['quality_score'] for r in successful_results if r['quality_score']]
            margins_of_safety = [r['margin_of_safety'] for r in successful_results 
                               if r['margin_of_safety'] is not None]
            
            results['summary_stats'] = {
                'avg_epv': sum(epv_values) / len(epv_values) if epv_values else 0,
                'avg_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                'avg_margin_of_safety': sum(margins_of_safety) / len(margins_of_safety) if margins_of_safety else 0,
                'undervalued_count': len([m for m in margins_of_safety if m > 0]),
                'high_quality_count': len([q for q in quality_scores if q > 0.7])
            }
        
        # Export summary if requested
        if export_summary and successful_results:
            import pandas as pd
            from datetime import date
            
            summary_data = []
            for symbol, data in results['results'].items():
                if 'error' not in data:
                    summary_data.append({
                        'Symbol': symbol,
                        'Company': data['company_name'],
                        'EPV_Per_Share': data['epv_per_share'],
                        'Current_Price': data['current_price'],
                        'Margin_of_Safety': data['margin_of_safety'],
                        'Quality_Score': data['quality_score'],
                        'Cost_of_Capital': data['cost_of_capital']
                    })
            
            if summary_data:
                df = pd.DataFrame(summary_data)
                filename = f"exports/batch_analysis_{date.today().strftime('%Y%m%d')}.csv"
                df.to_csv(filename, index=False)
                results['export_file'] = filename
        
        self.logger.info(f"Batch analysis complete: {results['successful_analyses']} successful, "
                        f"{results['failed_analyses']} failed")
        return results
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()
    
    def clear_cache(self) -> int:
        """Clear all cached data"""
        return self.cache_manager.clear_all()

def main():
    """Main command-line interface"""
    parser = argparse.ArgumentParser(description="EPV Research Platform")
    parser.add_argument("command", choices=["analyze", "quick", "batch", "cache-stats", "clear-cache", "web", "api"],
                       help="Command to execute")
    parser.add_argument("--symbol", "-s", help="Stock symbol to analyze")
    parser.add_argument("--symbols", nargs="+", help="Multiple stock symbols for batch analysis")
    parser.add_argument("--peers", nargs="*", help="Peer company symbols for comparison")
    parser.add_argument("--years", "-y", type=int, default=10, help="Years of historical data")
    parser.add_argument("--export", "-e", choices=["json", "csv"], help="Export format")
    parser.add_argument("--port", "-p", type=int, default=8050, help="Port for web interface")
    
    args = parser.parse_args()
    
    # Setup
    setup_directories()
    setup_logging()
    
    platform = EPVResearchPlatform()
    
    try:
        if args.command == "analyze":
            if not args.symbol:
                print("Error: --symbol required for analyze command")
                return 1
            
            results = platform.analyze_stock(
                symbol=args.symbol,
                peer_symbols=args.peers,
                years=args.years,
                export_format=args.export
            )
            
            # Print summary
            print(f"\n=== EPV Analysis Results for {results['symbol']} ===")
            print(f"Company: {results['company_name']}")
            print(f"EPV per share: ${results['epv_per_share']:.2f}")
            if results['current_price']:
                print(f"Current price: ${results['current_price']:.2f}")
            if results['margin_of_safety'] is not None:
                print(f"Margin of safety: {results['margin_of_safety']:.1f}%")
            print(f"Quality score: {results['quality_score']:.2f}")
            print(f"Risk score: {results['risk_score']:.2f}")
            print(f"Recommendation: {results['recommendation']}")
            if results['target_price']:
                print(f"Target price: ${results['target_price']:.2f}")
            print(f"Confidence: {results['confidence_level']:.0%}")
            print(f"\nInvestment Thesis:\n{results['investment_thesis']}")
            
        elif args.command == "quick":
            if not args.symbol:
                print("Error: --symbol required for quick command")
                return 1
            
            results = platform.quick_epv(args.symbol)
            print(f"\n=== Quick EPV for {results['symbol']} ===")
            print(f"EPV per share: ${results['epv_per_share']:.2f}")
            if results['current_price']:
                print(f"Current price: ${results['current_price']:.2f}")
            if results['margin_of_safety'] is not None:
                print(f"Margin of safety: {results['margin_of_safety']:.1f}%")
            print(f"Quality score: {results['quality_score']:.2f}")
            
        elif args.command == "batch":
            if not args.symbols:
                print("Error: --symbols required for batch command")
                return 1
            
            results = platform.batch_analysis(args.symbols)
            print(f"\n=== Batch Analysis Results ===")
            print(f"Analyzed: {len(args.symbols)} symbols")
            print(f"Successful: {results['successful_analyses']}")
            print(f"Failed: {results['failed_analyses']}")
            
            if results['summary_stats']:
                stats = results['summary_stats']
                print(f"\nSummary Statistics:")
                print(f"Average EPV: ${stats['avg_epv']:.2f}")
                print(f"Average Quality: {stats['avg_quality']:.2f}")
                print(f"Average Margin of Safety: {stats['avg_margin_of_safety']:.1f}%")
                print(f"Undervalued stocks: {stats['undervalued_count']}")
                print(f"High quality stocks: {stats['high_quality_count']}")
            
        elif args.command == "cache-stats":
            stats = platform.get_cache_stats()
            print(f"\n=== Cache Statistics ===")
            print(f"Total entries: {stats['total_entries']}")
            print(f"Total size: {stats['total_size_bytes']:,} bytes")
            print(f"Expired entries: {stats['expired_entries']}")
            
        elif args.command == "clear-cache":
            cleared = platform.clear_cache()
            print(f"Cleared {cleared} cache entries")
            
        elif args.command == "web":
            print(f"Starting web interface on port {args.port}...")
            from ui.web_app import create_app
            app = create_app(platform)
            app.run(host="127.0.0.1", port=args.port, debug=True)
        
        elif args.command == "api":
            print(f"Starting API server on port {args.port}...")
            import uvicorn
            uvicorn.run("api.main:app", host="0.0.0.0", port=args.port, reload=True)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
