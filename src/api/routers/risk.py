"""
Risk analysis API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging

from src.analysis.risk import calc_risk

logger = logging.getLogger(__name__)
router = APIRouter()


class RiskRequest(BaseModel):
    prices: List[float]


class RiskResponse(BaseModel):
    VaR99: float
    Sharpe: float
    Alpha: float


@router.post("/risk/metrics", response_model=RiskResponse)
async def calculate_risk_metrics(request: RiskRequest):
    """
    Calculate risk metrics for a given price series.
    
    Args:
        request: Request containing list of prices
        
    Returns:
        Risk metrics including VaR99, Sharpe ratio, and Alpha
    """
    try:
        if not request.prices:
            raise HTTPException(status_code=400, detail="Prices list cannot be empty")
        
        if len(request.prices) < 2:
            raise HTTPException(status_code=400, detail="At least 2 price points required for risk calculation")
        
        # Validate price values
        for price in request.prices:
            if price <= 0:
                raise HTTPException(status_code=400, detail="All prices must be positive")
        
        logger.info(f"Calculating risk metrics for {len(request.prices)} price points")
        
        # Calculate risk metrics
        risk_metrics = calc_risk(request.prices)
        
        logger.info(f"Risk metrics calculated: {risk_metrics}")
        
        return RiskResponse(**risk_metrics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating risk metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error calculating risk metrics")