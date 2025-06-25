"""
FastAPI application providing REST endpoints for EPV Research Platform
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime

from analysis.epv_calculator import EPVCalculator
from analysis.research_generator import ResearchGenerator
from analysis.portfolio_manager import PortfolioManager
from data.data_collector import DataCollector
from config.config import config

logger = logging.getLogger(__name__)

app = FastAPI(
    title="EPV Research Platform API",
    description="REST API for Earnings Power Value analysis and financial research",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_collector = DataCollector()
epv_calculator = EPVCalculator()
research_generator = ResearchGenerator()
portfolio_manager = PortfolioManager()

class AnalysisRequest(BaseModel):
    symbol: str
    years: int = 5
    peers: Optional[List[str]] = None
    analysis_type: str = "quick"

class BatchAnalysisRequest(BaseModel):
    symbols: List[str]
    years: int = 5

class PortfolioOptimizationRequest(BaseModel):
    symbols: List[str]
    weights: Optional[List[float]] = None
    target_return: Optional[float] = None

@app.get("/")
async def root():
    """Root endpoint providing API information"""
    return {
        "message": "EPV Research Platform API",
        "version": "1.0.0",
        "endpoints": {
            "analysis": "/api/v1/analysis/{symbol}",
            "batch": "/api/v1/batch",
            "portfolio": "/api/v1/portfolio/optimize",
            "company": "/api/v1/company/{symbol}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/analysis/{symbol}")
async def analyze_stock(symbol: str, request: AnalysisRequest):
    """
    Perform EPV analysis on a single stock
    """
    try:
        symbol = symbol.upper()
        
        # Collect financial data
        logger.info(f"Starting analysis for {symbol}")
        data = await asyncio.get_event_loop().run_in_executor(
            None, data_collector.collect_comprehensive_data, symbol, request.years
        )
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Calculate EPV
        epv_result = epv_calculator.calculate_epv(
            symbol=symbol,
            income_statements=data.income_statements,
            balance_sheets=data.balance_sheets,
            cash_flow_statements=data.cash_flow_statements,
            financial_ratios=data.financial_ratios,
            current_price=data.current_price,
            company_profile=data.company_profile
        )
        
        result = {
            "symbol": symbol,
            "analysis_date": datetime.now().isoformat(),
            "current_price": data.current_price,
            "epv_per_share": epv_result.epv_per_share,
            "normalized_earnings": epv_result.normalized_earnings,
            "cost_of_capital": epv_result.cost_of_capital,
            "margin_of_safety": epv_result.margin_of_safety,
            "quality_score": epv_result.quality_score,
            "risk_score": epv_result.risk_score,
            "investment_thesis": epv_result.investment_thesis if request.analysis_type == "full" else None,
            "risk_factors": epv_result.risk_factors if request.analysis_type == "full" else None,
        }
        
        # Add peer analysis if requested
        if request.peers and request.analysis_type == "full":
            peer_analysis = []
            for peer_symbol in request.peers[:5]:  # Limit to 5 peers
                try:
                    peer_data = await asyncio.get_event_loop().run_in_executor(
                        None, data_collector.collect_comprehensive_data, peer_symbol, request.years
                    )
                    if peer_data:
                        peer_epv = epv_calculator.calculate_epv(
                            symbol=peer_symbol,
                            income_statements=peer_data.income_statements,
                            balance_sheets=peer_data.balance_sheets,
                            cash_flow_statements=peer_data.cash_flow_statements,
                            financial_ratios=peer_data.financial_ratios,
                            current_price=peer_data.current_price,
                            company_profile=peer_data.company_profile
                        )
                        peer_analysis.append({
                            "symbol": peer_symbol,
                            "epv_per_share": peer_epv.epv_per_share,
                            "current_price": peer_data.current_price,
                            "margin_of_safety": peer_epv.margin_of_safety,
                            "quality_score": peer_epv.quality_score
                        })
                except Exception as e:
                    logger.warning(f"Failed to analyze peer {peer_symbol}: {e}")
            
            result["peer_analysis"] = peer_analysis
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batch")
async def batch_analysis(request: BatchAnalysisRequest):
    """
    Perform batch EPV analysis on multiple stocks
    """
    try:
        results = []
        summary_stats = {
            "total_analyzed": 0,
            "successful_analyses": 0,
            "average_epv": 0,
            "undervalued_count": 0,
            "high_quality_count": 0
        }
        
        epv_values = []
        
        for symbol in request.symbols[:20]:  # Limit to 20 symbols
            try:
                symbol = symbol.upper().strip()
                data = await asyncio.get_event_loop().run_in_executor(
                    None, data_collector.collect_comprehensive_data, symbol, request.years
                )
                
                if data:
                    epv_result = epv_calculator.calculate_epv(
                        symbol=symbol,
                        income_statements=data.income_statements,
                        balance_sheets=data.balance_sheets,
                        cash_flow_statements=data.cash_flow_statements,
                        financial_ratios=data.financial_ratios,
                        current_price=data.current_price,
                        company_profile=data.company_profile
                    )
                    
                    result = {
                        "symbol": symbol,
                        "current_price": data.current_price,
                        "epv_per_share": epv_result.epv_per_share,
                        "margin_of_safety": epv_result.margin_of_safety,
                        "quality_score": epv_result.quality_score,
                        "risk_score": epv_result.risk_score,
                        "recommendation": "BUY" if epv_result.margin_of_safety > 0.2 else "HOLD" if epv_result.margin_of_safety > 0 else "SELL"
                    }
                    
                    results.append(result)
                    summary_stats["successful_analyses"] += 1
                    
                    if epv_result.epv_per_share:
                        epv_values.append(epv_result.epv_per_share)
                    
                    if epv_result.margin_of_safety > 0:
                        summary_stats["undervalued_count"] += 1
                    
                    if epv_result.quality_score and epv_result.quality_score > 7:
                        summary_stats["high_quality_count"] += 1
                
            except Exception as e:
                logger.warning(f"Failed to analyze {symbol}: {e}")
            
            summary_stats["total_analyzed"] += 1
        
        if epv_values:
            summary_stats["average_epv"] = sum(epv_values) / len(epv_values)
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "summary": summary_stats,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/company/{symbol}")
async def get_company_profile(symbol: str):
    """
    Get detailed company profile and financial data
    """
    try:
        symbol = symbol.upper()
        data = await asyncio.get_event_loop().run_in_executor(
            None, data_collector.collect_comprehensive_data, symbol, 5
        )
        
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Convert dataclasses to dicts for JSON serialization
        from dataclasses import asdict
        
        return {
            "symbol": symbol,
            "company_profile": asdict(data.company_profile) if data.company_profile else None,
            "current_price": data.current_price,
            "market_cap": data.market_cap,
            "latest_financials": {
                "income_statement": asdict(data.income_statements[0]) if data.income_statements else None,
                "balance_sheet": asdict(data.balance_sheets[0]) if data.balance_sheets else None,
                "cash_flow": asdict(data.cash_flow_statements[0]) if data.cash_flow_statements else None,
                "ratios": asdict(data.financial_ratios[0]) if data.financial_ratios else None
            }
        }
        
    except Exception as e:
        logger.error(f"Company profile request failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """
    Optimize portfolio allocation using modern portfolio theory
    """
    try:
        # Collect data for all symbols
        portfolio_data = {}
        for symbol in request.symbols:
            data = await asyncio.get_event_loop().run_in_executor(
                None, data_collector.collect_comprehensive_data, symbol.upper(), 3
            )
            if data:
                portfolio_data[symbol.upper()] = data
        
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="No valid symbols found")
        
        # Perform portfolio optimization
        optimization_result = portfolio_manager.optimize_portfolio(
            portfolio_data,
            target_return=request.target_return
        )
        
        return {
            "optimization_date": datetime.now().isoformat(),
            "symbols": list(portfolio_data.keys()),
            "optimal_weights": optimization_result.get("weights", {}),
            "expected_return": optimization_result.get("expected_return"),
            "expected_volatility": optimization_result.get("expected_volatility"),
            "sharpe_ratio": optimization_result.get("sharpe_ratio"),
            "efficient_frontier": optimization_result.get("efficient_frontier", [])
        }
        
    except Exception as e:
        logger.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)