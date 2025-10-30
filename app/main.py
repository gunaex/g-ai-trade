from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime

from app.db import engine, Base, get_db
from app.ai.decision import AIDecisionEngine
from app.models import Trade, GridBot, DCABot
from sqlalchemy.orm import Session

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="G-AI-TRADE API",
    version="1.0.0",
    description="AI-Powered Crypto Trading System"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI Engine
ai_engine = AIDecisionEngine()

# Pydantic Models
class TradeRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    amount: float
    price: Optional[float] = None

class GridBotRequest(BaseModel):
    symbol: str
    lower_price: float
    upper_price: float
    grid_levels: int = 25
    amount_per_grid: float = 50

class DCABotRequest(BaseModel):
    symbol: str
    amount_per_period: float = 50
    interval_days: int = 7
    total_periods: int = 12

# ==================== ROUTES ====================

@app.get("/")
async def root():
    """Serve frontend"""
    if os.path.exists("dist/index.html"):
        return FileResponse("dist/index.html")
    return {"message": "G-AI-TRADE API v1.0 - Frontend not built yet"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/decision/{symbol}")
async def get_ai_decision(
    symbol: str,
    currency: str = "USD",
    db: Session = Depends(get_db)
):
    """
    Get AI trading decision for a symbol
    Returns: action, principle, predicted_pl, confidence
    """
    try:
        decision = await ai_engine.analyze(symbol, currency)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/trade")
async def execute_trade(
    trade_request: TradeRequest,
    db: Session = Depends(get_db)
):
    """
    Execute manual trade
    Uses BINANCE TH API v1.0.0 for trading operations
    """
    try:
        from app.binance_client import get_binance_th_client
        
        # Convert symbol to Binance format (remove slash if present)
        symbol = trade_request.symbol.replace('/', '')
        
        # Create trade record
        trade = Trade(
            symbol=trade_request.symbol,
            side=trade_request.side,
            amount=trade_request.amount,
            price=trade_request.price,
            status="pending",
            timestamp=datetime.utcnow()
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        # Execute trade via Binance TH API v1
        client = get_binance_th_client()
        
        if trade_request.price:
            # LIMIT order
            order = client.create_order(
                symbol=symbol,
                side=trade_request.side,
                order_type='LIMIT',
                quantity=trade_request.amount,
                price=trade_request.price
            )
        else:
            # MARKET order
            order = client.create_order(
                symbol=symbol,
                side=trade_request.side,
                order_type='MARKET',
                quantity=trade_request.amount
            )
        
        # Update trade record
        trade.status = order.get('status', 'filled')
        trade.filled_price = float(order.get('price', trade_request.price or 0))
        db.commit()
        
        return {
            "order_id": trade.id,
            "exchange_order_id": order.get('orderId'),
            "status": trade.status,
            "symbol": trade.symbol,
            "side": trade.side,
            "amount": trade.amount,
            "price": trade.filled_price
        }
    except Exception as e:
        trade.status = "failed"
        db.commit()
        print(f"Trade execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/grid-bot/{symbol}")
async def start_grid_bot(
    symbol: str,
    config: GridBotRequest,
    db: Session = Depends(get_db)
):
    """
    Start Grid Trading Bot
    """
    try:
        grid_bot = GridBot(
            symbol=symbol,
            lower_price=config.lower_price,
            upper_price=config.upper_price,
            grid_levels=config.grid_levels,
            amount_per_grid=config.amount_per_grid,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(grid_bot)
        db.commit()
        db.refresh(grid_bot)
        
        # Calculate grid levels
        price_range = config.upper_price - config.lower_price
        step = price_range / config.grid_levels
        levels = [
            config.lower_price + (i * step) 
            for i in range(config.grid_levels + 1)
        ]
        
        return {
            "status": "started",
            "bot_id": grid_bot.id,
            "symbol": symbol,
            "levels": levels,
            "grid_count": len(levels),
            "predicted_pl_percent": 3.5  # Simplified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dca-bot/{symbol}")
async def start_dca_bot(
    symbol: str,
    config: DCABotRequest,
    db: Session = Depends(get_db)
):
    """
    Start DCA (Dollar Cost Averaging) Bot
    """
    try:
        dca_bot = DCABot(
            symbol=symbol,
            amount_per_period=config.amount_per_period,
            interval_days=config.interval_days,
            total_periods=config.total_periods,
            completed_periods=0,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(dca_bot)
        db.commit()
        db.refresh(dca_bot)
        
        return {
            "status": "scheduled",
            "bot_id": dca_bot.id,
            "symbol": symbol,
            "interval": f"{config.interval_days}d",
            "amount_per_buy": config.amount_per_period,
            "total_investment": config.amount_per_period * config.total_periods,
            "next_buy_date": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/whale/{symbol}")
async def get_whale_movements(symbol: str):
    """
    Get whale movement data for symbol
    """
    try:
        # Simplified whale tracking
        # In production, integrate with on-chain data providers
        movements = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "amount": 125.5,
                "type": "buy",
                "wallet": "0x1234...5678",
                "usd_value": 8500000
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "amount": 95.2,
                "type": "sell",
                "wallet": "0x8765...4321",
                "usd_value": 6450000
            }
        ]
        
        # Calculate whale score (0-1)
        buy_volume = sum(m["amount"] for m in movements if m["type"] == "buy")
        sell_volume = sum(m["amount"] for m in movements if m["type"] == "sell")
        whale_score = buy_volume / (buy_volume + sell_volume) if (buy_volume + sell_volume) > 0 else 0.5
        
        return {
            "symbol": symbol,
            "movements": movements,
            "whale_score": round(whale_score, 2),
            "net_flow": round(buy_volume - sell_volume, 2),
            "interpretation": "Bullish" if whale_score > 0.6 else "Bearish" if whale_score < 0.4 else "Neutral"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str, currency: str = "USD"):
    """
    Get current market data for symbol
    Uses GLOBAL Binance API for reliable market data
    """
    try:
        from app.binance_client import get_market_data_client
        
        exchange = get_market_data_client()
        
        # Convert symbol format if needed (BTCUSDT -> BTC/USDT)
        ccxt_symbol = symbol
        if '/' not in symbol:
            if 'USDT' in symbol:
                ccxt_symbol = symbol.replace('USDT', '/USDT')
            elif 'USD' in symbol:
                ccxt_symbol = symbol.replace('USD', '/USD')
        
        # Get ticker data
        ticker = exchange.fetch_ticker(ccxt_symbol)
        
        # Get OHLCV data
        ohlcv = exchange.fetch_ohlcv(ccxt_symbol, '1h', limit=24)
        
        return {
            "symbol": symbol,
            "price": ticker['last'],
            "change_24h": ticker['percentage'],
            "volume_24h": ticker['quoteVolume'],
            "high_24h": ticker['high'],
            "low_24h": ticker['low'],
            "ohlcv": ohlcv,
            "currency": currency
        }
    except Exception as e:
        print(f"Market data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/api/portfolio")
async def get_portfolio(db: Session = Depends(get_db)):
    """
    Get current portfolio status
    """
    try:
        trades = db.query(Trade).filter(Trade.status == "filled").all()
        
        # Calculate portfolio metrics
        total_invested = sum(t.amount * t.filled_price for t in trades if t.side == "BUY")
        total_returns = sum(t.amount * t.filled_price for t in trades if t.side == "SELL")
        
        return {
            "total_trades": len(trades),
            "total_invested": round(total_invested, 2),
            "total_returns": round(total_returns, 2),
            "profit_loss": round(total_returns - total_invested, 2),
            "roi_percent": round(((total_returns - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files for production (only if built)
if os.path.exists("dist") and os.path.exists("dist/assets"):
    try:
        app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
    except Exception as e:
        pass  # Ignore in development

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
