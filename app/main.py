from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Literal
import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, func

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from app.db import engine, Base, get_db
from app.ai.decision import AIDecisionEngine
from app.models import Trade, GridBot, DCABot
from sqlalchemy.orm import Session
from app.trading_bot import ai_trading_bot
from app.ai.advanced_modules import AdvancedAITradingEngine

# Add new imports
from app.backtesting.backtesting_engine import (
    BacktestingEngine, 
    load_historical_data
)
from app.backtesting.onchain_filter import (
    OnChainFilter,
    MockOnChainProvider,
    IntegratedDecisionEngine
)
from typing import Literal, Dict

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

@app.get("/api/performance/{period}")
async def get_performance(
    period: Literal["today", "week", "month", "year"],
    db: Session = Depends(get_db)
):
    """
    Get REAL trading performance from database
    Supports: today, week, month, year
    """
    try:
        # Calculate date range
        now = datetime.utcnow()
        
        if period == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # Query REAL completed trades from database
        trades = db.query(Trade).filter(
            and_(
                Trade.timestamp >= start_date,
                Trade.timestamp <= now,
                Trade.status.in_(["filled", "completed"])  # Only successful trades
            )
        ).all()
        
        # Check if we have data
        if not trades or len(trades) == 0:
            return {
                "period": period,
                "has_data": False,
                "profit_loss": 0,
                "profit_loss_percent": 0,
                "total_trades": 0,
                "win_rate": 0,
                "best_trade": 0,
                "worst_trade": 0,
                "message": "No trading data available for this period"
            }
        
        # Calculate REAL metrics from trades
        profit_losses = []
        buy_trades = {}  # Track buy prices for calculating P/L
        
        for trade in trades:
            if not trade.filled_price or not trade.amount:
                continue
                
            trade_value = trade.amount * trade.filled_price
            
            if trade.side == "BUY":
                # Store buy for later P/L calculation
                if trade.symbol not in buy_trades:
                    buy_trades[trade.symbol] = []
                buy_trades[trade.symbol].append({
                    'price': trade.filled_price,
                    'amount': trade.amount,
                    'value': trade_value
                })
            
            elif trade.side == "SELL":
                # Calculate P/L for sell
                if trade.symbol in buy_trades and len(buy_trades[trade.symbol]) > 0:
                    # Get average buy price (FIFO)
                    buy_trade = buy_trades[trade.symbol][0]
                    
                    # P/L = (sell_price - buy_price) * amount
                    pl = (trade.filled_price - buy_trade['price']) * min(trade.amount, buy_trade['amount'])
                    profit_losses.append(pl)
                    
                    # Update or remove buy trade
                    if trade.amount >= buy_trade['amount']:
                        buy_trades[trade.symbol].pop(0)
                    else:
                        buy_trades[trade.symbol][0]['amount'] -= trade.amount
        
        # Calculate metrics
        total_trades = len(trades)
        total_profit_loss = sum(profit_losses) if profit_losses else 0
        
        # Win rate calculation
        winning_trades = sum(1 for pl in profit_losses if pl > 0)
        win_rate = (winning_trades / len(profit_losses) * 100) if profit_losses else 0
        
        # Best and worst trades
        best_trade = max(profit_losses) if profit_losses else 0
        worst_trade = min(profit_losses) if profit_losses else 0
        
        # Calculate percentage based on total invested
        total_invested = sum(
            t.amount * t.filled_price 
            for t in trades 
            if t.side == "BUY" and t.filled_price
        )
        
        profit_loss_percent = (
            (total_profit_loss / total_invested * 100) 
            if total_invested > 0 
            else 0
        )
        
        return {
            "period": period,
            "has_data": True,
            "profit_loss": round(total_profit_loss, 2),
            "profit_loss_percent": round(profit_loss_percent, 2),
            "total_trades": total_trades,
            "completed_rounds": len(profit_losses),  # จำนวนรอบที่เทรดสำเร็จ (BUY+SELL)
            "win_rate": round(win_rate, 1),
            "best_trade": round(best_trade, 2),
            "worst_trade": round(worst_trade, 2),
            "total_invested": round(total_invested, 2),
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat()
        }
        
    except Exception as e:
        print(f"Performance calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/performance/recent-trades")
async def get_recent_trades(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get recent trades for monitoring page
    """
    try:
        trades = db.query(Trade).order_by(
            Trade.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "trades": [
                {
                    "id": t.id,
                    "symbol": t.symbol,
                    "side": t.side,
                    "amount": t.amount,
                    "price": t.filled_price or t.price,
                    "status": t.status,
                    "timestamp": t.timestamp.isoformat()
                }
                for t in trades
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic Models สำหรับ Backtesting
class BacktestRequest(BaseModel):
    symbol: str
    timeframe: str = '5m'  # 1m, 5m, 15m, 1h, 4h, 1d
    days: int = 30
    initial_capital: float = 10000
    position_size_percent: float = 0.95

class BacktestResult(BaseModel):
    success: bool
    metrics: Optional[Dict] = None
    equity_curve: Optional[List[Dict]] = None
    trades: Optional[List[Dict]] = None
    error: Optional[str] = None

# Backtesting Endpoints
@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """
    รัน Backtesting สำหรับกลยุทธ์ AI
    
    Example:
    POST /api/backtest/run
    {
        "symbol": "BTC/USDT",
        "timeframe": "5m",
        "days": 30,
        "initial_capital": 10000
    }
    """
    try:
        # 1. โหลดข้อมูลย้อนหลัง
        logger.info(f"Loading historical data for {request.symbol}")
        data = await load_historical_data(
            symbol=request.symbol,
            timeframe=request.timeframe,
            days=request.days
        )
        
        if data.empty:
            raise HTTPException(
                status_code=400,
                detail="Failed to load historical data"
            )
        
        # 2. สร้าง AI Engine
        from app.ai.advanced_modules import AdvancedAITradingEngine
        ai_engine = AdvancedAITradingEngine()
        
        # 3. สร้าง Backtesting Engine
        backtest_engine = BacktestingEngine(
            symbol=request.symbol,
            data=data,
            ai_engine=ai_engine,
            initial_capital=request.initial_capital,
            position_size_percent=request.position_size_percent
        )
        
        # 4. รัน Backtest
        logger.info(f"Running backtest for {request.symbol}")
        metrics = await backtest_engine.run()
        
        # 5. Generate Tear Sheet (ใน console)
        backtest_engine.generate_tear_sheet()
        
        # 6. ดึงข้อมูลเพิ่มเติม
        equity_curve = backtest_engine.portfolio.get_equity_curve_df()
        equity_curve_json = equity_curve.to_dict('records')
        
        trades = backtest_engine.portfolio.trades
        
        return {
            "success": True,
            "metrics": metrics,
            "equity_curve": equity_curve_json,
            "trades": trades[-50:],  # ส่ง 50 trades ล่าสุด
            "config": {
                "symbol": request.symbol,
                "timeframe": request.timeframe,
                "days": request.days,
                "initial_capital": request.initial_capital,
                "data_points": len(data)
            }
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/status/{symbol}")
async def get_backtest_status(symbol: str):
    """
    เช็คสถานะ Backtest (สำหรับ long-running tests)
    """
    # TODO: Implement task queue (Celery/Redis) for long backtests
    return {
        "status": "not_implemented",
        "message": "Use /api/backtest/run for synchronous backtesting"
    }

@app.get("/api/backtest/presets")
async def get_backtest_presets():
    """
    ดึง Preset configurations สำหรับ Backtesting
    """
    return {
        "presets": [
            {
                "name": "Quick Test (7 days)",
                "symbol": "BTC/USDT",
                "timeframe": "5m",
                "days": 7,
                "initial_capital": 10000
            },
            {
                "name": "Short Term (30 days)",
                "symbol": "BTC/USDT",
                "timeframe": "15m",
                "days": 30,
                "initial_capital": 10000
            },
            {
                "name": "Medium Term (90 days)",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "days": 90,
                "initial_capital": 10000
            },
            {
                "name": "Long Term (180 days)",
                "symbol": "BTC/USDT",
                "timeframe": "4h",
                "days": 180,
                "initial_capital": 10000
            }
        ],
        "supported_symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
        "supported_timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"]
    }

@app.post("/api/onchain/analyze")
async def analyze_onchain(symbol: str):
    """
    วิเคราะห์ On-Chain Data สำหรับ symbol
    
    Example:
    POST /api/onchain/analyze?symbol=BTC/USDT
    """
    try:
        # สร้าง OnChain Filter (ใช้ Mock Provider)
        onchain_filter = OnChainFilter(provider=MockOnChainProvider())
        
        # วิเคราะห์
        analysis = await onchain_filter.analyze(symbol)
        
        return {
            "symbol": symbol,
            "status": analysis.status,
            "confidence": analysis.confidence,
            "veto_buy": analysis.veto_buy,
            "reasoning": analysis.reasoning,
            "metrics": {
                "exchange_netflow": analysis.metrics.exchange_netflow,
                "whale_transactions": analysis.metrics.whale_transactions,
                "whale_volume": analysis.metrics.whale_volume,
                "stablecoin_supply_ratio": analysis.metrics.stablecoin_supply_ratio,
                "timestamp": analysis.metrics.timestamp.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"OnChain analysis error: {e}")
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
@app.get("/api/account/balance")
async def get_account_balance():
    """
    Get account balances from Binance TH
    """
    try:
        from app.binance_client import get_binance_th_client
        
        client = get_binance_th_client()
        account = client.get_account()
        
        # Format response to match expected structure
        return {
            "balances": account.get('balances', [])
        }
    except Exception as e:
        print(f"Balance fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Force Trading Bot Endpoints
@app.post("/api/bot/ai-force/start")
async def start_ai_force_bot(
    symbol: str = "BTCUSDT",
    amount: float = 0.01,
    max_profit: float = 6.0,
    max_loss: float = 4.0
):
    """
    Start AI Force Trading Bot
    - Automatically buys when price drops
    - Automatically sells when price rises
    - Stops at 6% profit or 4% loss per day
    """
    try:
        result = await ai_trading_bot.start(symbol, amount, max_profit, max_loss)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bot/ai-force/stop")
async def stop_ai_force_bot():
    """Stop AI Force Trading Bot"""
    try:
        result = ai_trading_bot.stop()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bot/ai-force/status")
async def get_ai_force_bot_status():
    """Get AI Force Trading Bot status"""
    try:
        status = ai_trading_bot.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Initialize Advanced AI Engine
advanced_ai_engine = AdvancedAITradingEngine()

@app.get("/api/advanced-analysis/{symbol}")
async def get_advanced_analysis(
    symbol: str,
    currency: str = "USD"
):
    """
    Get Advanced AI Analysis using all 4 modules
    - Market Regime Filter
    - Sentiment Analysis
    - Dynamic Risk Management
    - Micro-Pattern Recognition
    """
    try:
        from app.binance_client import get_market_data_client
        
        client = get_market_data_client()
        
        # Fetch OHLCV data
        ohlcv_data = client.fetch_ohlcv(
            symbol.replace('USDT', '/USDT'),
            timeframe='1h',
            limit=200
        )
        
        # Convert to DataFrame
        import pandas as pd
        df = pd.DataFrame(
            ohlcv_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Fetch order book (optional)
        order_book = client.fetch_order_book(symbol.replace('USDT', '/USDT'))
        
        # Run Advanced AI Analysis
        analysis = advanced_ai_engine.analyze(symbol, df, order_book)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))