#!/usr/bin/env python3
"""
Simple demo API server for EPV Research Platform frontend
Provides mock data for demonstration purposes
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime

app = FastAPI(
    title="EPV Research Platform Demo API",
    description="Demo API for frontend testing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    symbol: str
    years: int = 5
    peers: Optional[List[str]] = None
    analysis_type: str = "quick"

class BatchAnalysisRequest(BaseModel):
    symbols: List[str]
    years: int = 5

def generate_mock_analysis(symbol: str, analysis_type: str = "quick"):
    """Generate mock analysis data for demo"""
    base_price = random.uniform(50, 300)
    epv_multiplier = random.uniform(0.8, 1.4)
    
    epv_per_share = base_price * epv_multiplier
    margin_of_safety = (epv_per_share - base_price) / base_price
    quality_score = random.uniform(4, 9)
    risk_score = random.uniform(2, 8)
    
    result = {
        "symbol": symbol,
        "analysis_date": datetime.now().isoformat(),
        "current_price": round(base_price, 2),
        "epv_per_share": round(epv_per_share, 2),
        "normalized_earnings": round(base_price * random.uniform(0.05, 0.15), 2),
        "cost_of_capital": round(random.uniform(0.08, 0.12), 4),
        "margin_of_safety": round(margin_of_safety, 4),
        "quality_score": round(quality_score, 2),
        "risk_score": round(risk_score, 2),
    }
    
    if analysis_type == "full":
        result.update({
            "investment_thesis": f"{symbol} shows strong fundamentals with sustainable competitive advantages. The company demonstrates consistent earnings power and efficient capital allocation.",
            "risk_factors": [
                "Market volatility and economic uncertainty",
                "Competitive pressure in core markets",
                "Regulatory changes affecting the industry",
                "Technology disruption risks"
            ]
        })
    
    return result

@app.get("/")
async def root():
    return {
        "message": "EPV Research Platform Demo API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/analysis/{symbol}")
async def analyze_stock(symbol: str, request: AnalysisRequest):
    """Mock stock analysis endpoint"""
    try:
        result = generate_mock_analysis(symbol.upper(), request.analysis_type)
        
        # Add peer analysis if requested
        if request.peers and request.analysis_type == "full":
            peer_analysis = []
            for peer_symbol in request.peers[:5]:
                peer_data = generate_mock_analysis(peer_symbol.upper())
                peer_analysis.append({
                    "symbol": peer_symbol.upper(),
                    "epv_per_share": peer_data["epv_per_share"],
                    "current_price": peer_data["current_price"],
                    "margin_of_safety": peer_data["margin_of_safety"],
                    "quality_score": peer_data["quality_score"]
                })
            result["peer_analysis"] = peer_analysis
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/batch")
async def batch_analysis(request: BatchAnalysisRequest):
    """Mock batch analysis endpoint"""
    try:
        results = []
        total_epv = 0
        undervalued_count = 0
        high_quality_count = 0
        
        for symbol in request.symbols[:20]:
            analysis = generate_mock_analysis(symbol.upper())
            
            recommendation = "BUY" if analysis["margin_of_safety"] > 0.2 else "HOLD" if analysis["margin_of_safety"] > 0 else "SELL"
            
            result = {
                "symbol": symbol.upper(),
                "current_price": analysis["current_price"],
                "epv_per_share": analysis["epv_per_share"],
                "margin_of_safety": analysis["margin_of_safety"],
                "quality_score": analysis["quality_score"],
                "risk_score": analysis["risk_score"],
                "recommendation": recommendation
            }
            
            results.append(result)
            total_epv += analysis["epv_per_share"]
            
            if analysis["margin_of_safety"] > 0:
                undervalued_count += 1
            if analysis["quality_score"] > 7:
                high_quality_count += 1
        
        summary = {
            "total_analyzed": len(request.symbols),
            "successful_analyses": len(results),
            "average_epv": round(total_epv / len(results) if results else 0, 2),
            "undervalued_count": undervalued_count,
            "high_quality_count": high_quality_count
        }
        
        return {
            "analysis_date": datetime.now().isoformat(),
            "summary": summary,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/company/{symbol}")
async def get_company_profile(symbol: str):
    """Mock company profile endpoint"""
    try:
        return {
            "symbol": symbol.upper(),
            "company_profile": {
                "company_name": f"{symbol.upper()} Corporation",
                "sector": "Technology",
                "industry": "Software",
                "description": f"Leading technology company in the {symbol.upper()} sector"
            },
            "current_price": round(random.uniform(50, 300), 2),
            "market_cap": round(random.uniform(1000000000, 2000000000000), 0),
            "latest_financials": {
                "income_statement": {"revenue": round(random.uniform(10000000, 100000000000), 0)},
                "balance_sheet": {"total_assets": round(random.uniform(50000000, 500000000000), 0)},
                "cash_flow": {"operating_cash_flow": round(random.uniform(1000000, 50000000000), 0)},
                "ratios": {"pe_ratio": round(random.uniform(10, 30), 2)}
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting EPV Research Platform Demo API...")
    print("📊 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)