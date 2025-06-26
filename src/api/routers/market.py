"""
API routes for market data
"""

from fastapi import APIRouter, HTTPException
import logging

from src.data.data_gateway import DataGateway

logger = logging.getLogger(__name__)
router = APIRouter()

data_gateway = DataGateway()


@router.get("/quotes/{symbol}")
async def get_quote(symbol: str):
    """
    Get the latest quote for a symbol.
    """
    quote = await data_gateway.get_quote(symbol.upper())
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote not found for {symbol}")
    return quote
