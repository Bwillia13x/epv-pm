"""
WebSocket endpoint for real-time market data
"""
import asyncio
import json
import logging
import random
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.data.data_gateway import DataGateway

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/ticker")
async def ticker_endpoint(websocket: WebSocket):
    await websocket.accept()
    data_gateway = DataGateway()
    
    try:
        while True:
            ticker_data = []
            
            # Get SPY quote
            spy_quote = await data_gateway.get_quote("SPY")
            if spy_quote:
                spy_price = spy_quote.get('price', 0.0)
                spy_change = spy_quote.get('change', 0.0)
                ticker_data.append({
                    "symbol": "SPY",
                    "price": float(spy_price),
                    "change": float(spy_change)
                })
            
            # Get VIX quote
            vix_quote = await data_gateway.get_quote("^VIX")
            if vix_quote:
                vix_price = vix_quote.get('price', 0.0)
                vix_change = vix_quote.get('change', 0.0)
                ticker_data.append({
                    "symbol": "^VIX",
                    "price": float(vix_price),
                    "change": float(vix_change)
                })
            
            # Send ticker data
            for data in ticker_data:
                await websocket.send_text(json.dumps(data))
            
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

@router.websocket("/ws/market")
async def market_data_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Simulate real-time market data
            data = {
                "SPY": round(random.uniform(400, 500), 2),
                "^VIX": round(random.uniform(12, 25), 2),
                "AAPL": round(random.uniform(150, 200), 2),
                "MSFT": round(random.uniform(300, 400), 2),
                "GOOGL": round(random.uniform(2500, 3000), 2),
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.info("Market WebSocket client disconnected")
