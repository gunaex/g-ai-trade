"""
AI Force Trade Bot
Auto Trading Engine with Take Profit & Stop Loss
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.binance_client import get_binance_th_client, get_market_data_client
from app.ai.decision import AIDecisionEngine
import logging

logger = logging.getLogger(__name__)

class AIForceTradingBot:
    def __init__(self):
        self.is_running = False
        self.th_client = get_binance_th_client()
        self.market_client = get_market_data_client()
        self.ai_engine = AIDecisionEngine()
        
        # Trading parameters
        self.symbol = 'BTCUSDT'
        self.trade_amount = 0.01  # Amount per trade
        self.max_profit_percent = 6.0  # Take profit at 6%
        self.max_loss_percent = 4.0   # Stop loss at 4%
        
        # Daily tracking
        self.daily_start_balance = 0
        self.current_balance = 0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        
        # Position tracking
        self.entry_price = None
        self.position_side = None  # 'BUY' or 'SELL'
        
    async def start(self, symbol: str, amount: float, max_profit: float, max_loss: float):
        """Start the AI Force Trading Bot"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.symbol = symbol
        self.trade_amount = amount
        self.max_profit_percent = max_profit
        self.max_loss_percent = max_loss
        self.is_running = True
        
        # Get starting balance
        account = self.th_client.get_account()
        balances = account.get('balances', [])
        usdt_balance = next((b for b in balances if b['asset'] == 'USDT'), None)
        
        if usdt_balance:
            self.daily_start_balance = float(usdt_balance['free'])
            self.current_balance = self.daily_start_balance
        
        logger.info(f"✅ AI Force Trading Bot Started - Symbol: {symbol}")
        logger.info(f"   Amount per trade: {amount}")
        logger.info(f"   Take Profit: {max_profit}% | Stop Loss: {max_loss}%")
        
        # Start trading loop
        asyncio.create_task(self._trading_loop())
        
        return {
            "status": "started",
            "symbol": symbol,
            "amount": amount,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "start_balance": self.daily_start_balance
        }
    
    def stop(self):
        """Stop the AI Force Trading Bot"""
        self.is_running = False
        logger.info("🛑 AI Force Trading Bot Stopped")
        
        profit_loss = self.current_balance - self.daily_start_balance
        profit_percent = (profit_loss / self.daily_start_balance * 100) if self.daily_start_balance > 0 else 0
        
        return {
            "status": "stopped",
            "daily_trades": self.daily_trades,
            "start_balance": self.daily_start_balance,
            "end_balance": self.current_balance,
            "profit_loss": profit_loss,
            "profit_percent": profit_percent
        }
    
    async def _trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                # Check if we need to reset daily stats
                self._check_daily_reset()
                
                # Check daily profit/loss limits
                if self._should_stop_trading():
                    logger.info("📊 Daily limit reached - stopping bot")
                    self.stop()
                    break
                
                # Get AI decision
                decision = await self.ai_engine.analyze(self.symbol, 'USD')
                
                # Get current market price
                ticker = self.market_client.fetch_ticker(
                    self.symbol.replace('USDT', '/USDT')
                )
                current_price = ticker['last']
                
                # Execute trading logic
                await self._execute_trading_logic(decision, current_price)
                
                # Wait 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Trading loop error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def _check_daily_reset(self):
        """Reset daily stats at midnight"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            logger.info("🔄 Daily reset - new trading day")
            self.daily_start_balance = self.current_balance
            self.daily_trades = 0
            self.last_reset_date = today
    
    def _should_stop_trading(self) -> bool:
        """Check if daily profit/loss limits are reached"""
        if self.daily_start_balance == 0:
            return False
        
        profit_loss_percent = ((self.current_balance - self.daily_start_balance) 
                               / self.daily_start_balance * 100)
        
        # Stop if reached profit target
        if profit_loss_percent >= self.max_profit_percent:
            logger.info(f"🎯 Take Profit reached: +{profit_loss_percent:.2f}%")
            return True
        
        # Stop if hit stop loss
        if profit_loss_percent <= -self.max_loss_percent:
            logger.warning(f"🛑 Stop Loss hit: {profit_loss_percent:.2f}%")
            return True
        
        return False
    
    async def _execute_trading_logic(self, decision: Dict, current_price: float):
        """Execute buy/sell based on AI decision"""
        action = decision.get('action')
        confidence = decision.get('confidence', 0)
        
        # Only trade if confidence > 60%
        if confidence < 0.6:
            logger.debug(f"⏸️  Low confidence ({confidence*100:.0f}%) - waiting...")
            return
        
        # BUY signal
        if action == 'BUY' and self.position_side != 'BUY':
            await self._execute_buy(current_price)
        
        # SELL signal
        elif action == 'SELL' and self.position_side == 'BUY':
            await self._execute_sell(current_price)
    
    async def _execute_buy(self, price: float):
        """Execute buy order"""
        try:
            logger.info(f"🟢 BUY Signal - Executing buy at {price}")
            
            order = self.th_client.create_order(
                symbol=self.symbol,
                side='BUY',
                order_type='MARKET',
                quantity=self.trade_amount
            )
            
            self.entry_price = price
            self.position_side = 'BUY'
            self.daily_trades += 1
            
            logger.info(f"✅ Buy order executed: {order.get('orderId')}")
            
        except Exception as e:
            logger.error(f"❌ Buy order failed: {e}")
    
    async def _execute_sell(self, price: float):
        """Execute sell order"""
        try:
            logger.info(f"🔴 SELL Signal - Executing sell at {price}")
            
            order = self.th_client.create_order(
                symbol=self.symbol,
                side='SELL',
                order_type='MARKET',
                quantity=self.trade_amount
            )
            
            # Calculate profit/loss
            if self.entry_price:
                profit_percent = ((price - self.entry_price) / self.entry_price * 100)
                profit_amount = self.trade_amount * price - self.trade_amount * self.entry_price
                
                logger.info(f"💰 Trade closed: {profit_percent:+.2f}% (${profit_amount:+.2f})")
                
                # Update balance
                self.current_balance += profit_amount
            
            self.entry_price = None
            self.position_side = None
            self.daily_trades += 1
            
            logger.info(f"✅ Sell order executed: {order.get('orderId')}")
            
        except Exception as e:
            logger.error(f"❌ Sell order failed: {e}")
    
    def get_status(self) -> Dict:
        """Get current bot status"""
        profit_loss = self.current_balance - self.daily_start_balance
        profit_percent = (profit_loss / self.daily_start_balance * 100) if self.daily_start_balance > 0 else 0
        
        return {
            "is_running": self.is_running,
            "symbol": self.symbol,
            "daily_trades": self.daily_trades,
            "start_balance": self.daily_start_balance,
            "current_balance": self.current_balance,
            "profit_loss": profit_loss,
            "profit_percent": profit_percent,
            "position_side": self.position_side,
            "entry_price": self.entry_price,
            "max_profit": self.max_profit_percent,
            "max_loss": self.max_loss_percent
        }


# Global bot instance
ai_trading_bot = AIForceTradingBot()
