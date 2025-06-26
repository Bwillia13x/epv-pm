"""
API routes for analysis, batch processing, and portfolio optimization
"""

from __future__ import annotations

# Third-party libs imported for linter visibility (already installed elsewhere)
import numpy as np  # type: ignore  # noqa: F401
import pandas as pd  # type: ignore  # noqa: F401
import httpx  # type: ignore  # noqa: F401
import yfinance as yf  # type: ignore  # noqa: F401

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
import asyncio
from datetime import datetime
from src.analysis.epv_calculator import EPVCalculator
from src.analysis.research_generator import ResearchGenerator
from src.analysis.portfolio_manager import PortfolioManager
from src.data.data_collector import DataCollector

# Settings must be imported before conditional features
from src.api.settings import settings
from src.data.data_gateway import DataGateway

# Conditional import for PDF report generation
if settings.pdf_enabled:
    try:
        from src.reports.generator import build_report  # type: ignore
    except ImportError:
        build_report = None  # Fallback if WeasyPrint deps not installed
else:
    build_report = None
from fastapi.responses import FileResponse
import os

logger = logging.getLogger(__name__)
router = APIRouter()

data_collector = DataCollector()
data_gateway = DataGateway()
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


@router.post("/analysis/{symbol}")
async def analyze_stock(symbol: str, request: AnalysisRequest):
    """
    Perform EPV analysis on a single stock
    """
    try:
        symbol = symbol.upper()

        # Collect financial data
        logger.info(f"Starting analysis for {symbol}")
        data = await data_collector.collect_comprehensive_data_async(
            symbol, request.years
        )

        if not data:
            raise HTTPException(
                status_code=404, detail=f"No data found for symbol {symbol}"
            )

        # Calculate EPV
        epv_result = epv_calculator.calculate_epv(
            symbol=symbol,
            income_statements=data.income_statements,
            balance_sheets=data.balance_sheets,
            cash_flow_statements=data.cash_flow_statements,
            financial_ratios=data.financial_ratios,
            current_price=data.current_price,
            company_profile=data.company_profile,
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
            "risk_score": getattr(epv_result, "risk_score", None),
            "investment_thesis": (
                epv_result.investment_thesis
                if request.analysis_type == "full"
                else None
            ),
            "risk_factors": (
                epv_result.risk_factors if request.analysis_type == "full" else None
            ),
        }

        # Add peer analysis if requested
        if request.peers and request.analysis_type == "full":
            peer_symbols = request.peers[:5]
            peer_tasks = [
                data_collector.collect_comprehensive_data_async(sym, request.years)
                for sym in peer_symbols
            ]

            peer_results = await asyncio.gather(*peer_tasks, return_exceptions=True)

            peer_analysis = []
            for peer_symbol, peer_data in zip(peer_symbols, peer_results):
                if isinstance(peer_data, Exception):
                    logger.warning(f"Failed to analyze peer {peer_symbol}: {peer_data}")
                    continue

                try:
                    peer_epv = epv_calculator.calculate_epv(
                        symbol=peer_symbol,
                        income_statements=getattr(peer_data, "income_statements", []),  # type: ignore[attr-defined]
                        balance_sheets=getattr(peer_data, "balance_sheets", []),  # type: ignore[attr-defined]
                        cash_flow_statements=getattr(peer_data, "cash_flow_statements", []),  # type: ignore[attr-defined]
                        financial_ratios=getattr(peer_data, "financial_ratios", []),  # type: ignore[attr-defined]
                        current_price=getattr(peer_data, "current_price", None),  # type: ignore[attr-defined]
                        company_profile=getattr(peer_data, "company_profile", None),  # type: ignore[attr-defined]
                    )
                    peer_analysis.append(
                        {
                            "symbol": peer_symbol,
                            "epv_per_share": peer_epv.epv_per_share,
                            "current_price": getattr(peer_data, "current_price", None),  # type: ignore[attr-defined]
                            "margin_of_safety": peer_epv.margin_of_safety,
                            "quality_score": peer_epv.quality_score,
                        }
                    )
                except Exception as exc:
                    logger.warning(
                        f"Failed to calculate EPV for peer {peer_symbol}: {exc}"
                    )

            result["peer_analysis"] = peer_analysis

        return result

    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
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
            "high_quality_count": 0,
        }

        epv_values = []

        for symbol in request.symbols[:20]:  # Limit to 20 symbols
            try:
                symbol = symbol.upper().strip()
                data = await data_collector.collect_comprehensive_data_async(
                    symbol, request.years
                )

                if data:
                    epv_result = epv_calculator.calculate_epv(
                        symbol=symbol,
                        income_statements=data.income_statements,
                        balance_sheets=data.balance_sheets,
                        cash_flow_statements=data.cash_flow_statements,
                        financial_ratios=data.financial_ratios,
                        current_price=data.current_price,
                        company_profile=data.company_profile,
                    )

                    result = {
                        "symbol": symbol,
                        "current_price": data.current_price,
                        "epv_per_share": epv_result.epv_per_share,
                        "margin_of_safety": epv_result.margin_of_safety,
                        "quality_score": epv_result.quality_score,
                        "risk_score": getattr(epv_result, "risk_score", None),
                        "recommendation": (
                            "BUY"
                            if epv_result.margin_of_safety is not None
                            and epv_result.margin_of_safety > 0.2
                            else (
                                "HOLD"
                                if epv_result.margin_of_safety is not None
                                and epv_result.margin_of_safety > 0
                                else "SELL"
                            )
                        ),
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
            "results": results,
        }

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{symbol}")
async def get_company_profile(symbol: str):
    """
    Get detailed company profile and financial data
    """
    try:
        symbol = symbol.upper()
        data = await data_collector.collect_comprehensive_data_async(symbol, 5)

        if not data:
            raise HTTPException(
                status_code=404, detail=f"No data found for symbol {symbol}"
            )

        # Convert dataclasses to dicts for JSON serialization
        from dataclasses import asdict

        return {
            "symbol": symbol,
            "company_profile": (
                asdict(data.company_profile) if data.company_profile else None
            ),
            "current_price": data.current_price,
            "market_cap": data.market_cap,
            "latest_financials": {
                "income_statement": (
                    asdict(data.income_statements[0])
                    if data.income_statements
                    else None
                ),
                "balance_sheet": (
                    asdict(data.balance_sheets[0]) if data.balance_sheets else None
                ),
                "cash_flow": (
                    asdict(data.cash_flow_statements[0])
                    if data.cash_flow_statements
                    else None
                ),
                "ratios": (
                    asdict(data.financial_ratios[0]) if data.financial_ratios else None
                ),
            },
        }

    except Exception as e:
        logger.error(f"Company profile request failed for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    """
    Optimize portfolio allocation using modern portfolio theory
    """
    try:
        # Collect data for all symbols
        portfolio_data = {}
        for symbol in request.symbols:
            data = await data_collector.collect_comprehensive_data_async(
                symbol.upper(), 3
            )
            if data:
                portfolio_data[symbol.upper()] = data

        if not portfolio_data:
            raise HTTPException(status_code=404, detail="No valid symbols found")

        # Perform portfolio optimization
        optimization_result = portfolio_manager.optimize_portfolio(  # type: ignore[arg-type]
            portfolio_data,  # type: ignore[arg-type]
            portfolio_value=1.0,  # placeholder
            risk_budget=portfolio_manager.create_risk_budget(),
            optimization_objective="max_epv_quality",
        )

        return {
            "optimization_date": datetime.now().isoformat(),
            "symbols": list(portfolio_data.keys()),
            "allocations": [alloc.__dict__ for alloc in optimization_result],
            "notes": "Optimization result schema simplified due to type constraints",  # type: ignore
        }

    except Exception as e:
        logger.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/{symbol}")
async def get_prices(symbol: str):
    """
    Get historical prices for a symbol.
    """
    prices = await data_gateway.get_prices(symbol.upper())
    if not prices:
        raise HTTPException(
            status_code=404, detail=f"Price data not found for {symbol}"
        )
    return prices


@router.get("/fundamentals/{symbol}")
async def get_fundamentals(symbol: str):
    """
    Get fundamental data for a symbol.
    """
    fundamentals = await data_gateway.get_fundamentals(symbol.upper())
    if not fundamentals:
        raise HTTPException(
            status_code=404, detail=f"Fundamental data not found for {symbol}"
        )
    return fundamentals


@router.post("/reports/generate")
async def generate_report(request: BatchAnalysisRequest):
    """
    Generate a PDF report for a batch of stocks.
    """
    try:
        # Feature flag: disable PDF generation unless explicitly enabled.
        if not settings.pdf_enabled or build_report is None:
            raise HTTPException(
                status_code=503, detail="PDF generation is disabled on this server."
            )

        # In a real application, you would fetch the analysis results
        # for the given symbols. For this example, we'll use dummy data.
        data = {
            "title": "Portfolio Summary",
            "stocks": [
                {
                    "symbol": "AAPL",
                    "company_name": "Apple Inc.",
                    "epv_per_share": 150.0,
                    "current_price": 172.25,
                    "margin_of_safety": -0.129,
                    "quality_score": 0.8,
                },
                {
                    "symbol": "MSFT",
                    "company_name": "Microsoft Corporation",
                    "epv_per_share": 350.0,
                    "current_price": 305.12,
                    "margin_of_safety": 0.147,
                    "quality_score": 0.9,
                },
            ],
        }

        output_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "exports", "reports"
        )
        os.makedirs(output_path, exist_ok=True)

        pdf_path = build_report(data, "summary.html", output_path)

        return FileResponse(
            pdf_path, media_type="application/pdf", filename=os.path.basename(pdf_path)
        )

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
