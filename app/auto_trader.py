"""
Auto Trading Engine
ระบบเทรดอัตโนมัติที่ทำงาน 24/7
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from collections import deque
import pandas as pd
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Trade, BotConfig
from app.binance_client import get_binance_th_client, get_market_data_client
from app.ai.advanced_modules import AdvancedAITradingEngine
from app.backtesting.onchain_filter import OnChainFilter, MockOnChainProvider

logger = logging.getLogger(__name__)


class AutoTrader:
    """
    Auto Trading Engine
    
    Features:
    - ทำงานอัตโนมัติ 24/7
    - AI Decision Making
    - Position Management (Entry/Exit/TP/SL)
    - Risk Management
    - Notification System
    """
    
    def __init__(self, 
                 db: Session,
                 config_id: int,
                 interval_seconds: int = 300):  # 5 minutes
        """
        Args:
            db: Database session
            config_id: Bot configuration ID
            interval_seconds: ความถี่ในการเช็ค (วินาที)
        """
        self.db = db
        self.config_id = config_id
        self.interval = interval_seconds
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.trading_client = get_binance_th_client()
        self.market_client = get_market_data_client()
        self.ai_engine = AdvancedAITradingEngine()
        self.onchain_filter = OnChainFilter(provider=MockOnChainProvider())
        
        # State
        self.is_running = False
        self.current_position: Optional[Dict] = None
        self.last_check_time = datetime.utcnow()
        
        # Activity Log (Keep last 100 activities)
        self.activity_log: deque = deque(maxlen=100)
        
        logger.info(f"🤖 AutoTrader initialized: {self.config.symbol} | Budget: {self.config.budget}")
        self._log_activity("🤖 AutoTrader Initialized", "info")
    
    def _load_config(self) -> BotConfig:
        """โหลดการตั้งค่า Bot จาก database"""
        config = self.db.query(BotConfig).filter(BotConfig.id == self.config_id).first()
        if not config:
            raise ValueError(f"Bot config {self.config_id} not found")
        return config
    
    def _log_activity(self, message: str, level: str = "info", data: Dict = None):
        """
        บันทึก Activity Log (ใช้ Server Local Time)
        
        Args:
            message: ข้อความ
            level: info, warning, error, success
            data: ข้อมูลเพิ่มเติม (optional)
        """
        activity = {
            "timestamp": datetime.now().isoformat(),  # Server local time
            "message": message,
            "level": level,
            "data": data or {}
        }
        self.activity_log.append(activity)
        
        # Log to console as well
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        elif level == "success":
            logger.info(f"✅ {message}")
        else:
            logger.info(message)
    
    def get_activity_log(self, limit: int = 10) -> List[Dict]:
        """ดึง Activity Log ล่าสุด"""
        return list(self.activity_log)[-limit:]
    
    async def start(self):
        """เริ่มการทำงาน Auto Trading"""
        self.is_running = True
        logger.info("🚀 Auto Trading Started!")
        self._log_activity("🚀 Auto Trading Started!", "success")
        
        try:
            while self.is_running:
                await self._trading_cycle()
                await asyncio.sleep(self.interval)
        
        except Exception as e:
            logger.error(f"❌ Auto Trading Error: {e}")
            self._log_activity(f"❌ Auto Trading Error: {e}", "error")
            self.is_running = False
    
    def stop(self):
        """หยุดการทำงาน"""
        # Log stop activity before flipping the flag
        try:
            self._log_activity("🛑 Auto Trading Stopped", "info")
        except Exception:
            # Ensure stopping never fails due to logging
            pass
        self.is_running = False
        logger.info("🛑 Auto Trading Stopped")
    
    async def _trading_cycle(self):
        """
        Trading Cycle (Main Loop)
        
        1. ดึงข้อมูลตลาด
        2. เช็ค Position ปัจจุบัน
        3. ถ้ามี Position → Monitor TP/SL
        4. ถ้าไม่มี Position → หา Entry Signal
        5. Execute Order (ถ้ามี)
        6. บันทึก Log
        """
        try:
            logger.info(f"⏱️  [{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Trading Cycle")
            self._log_activity("⏱️  Trading Cycle Started", "info")
            
            # 1. ดึงข้อมูลตลาด (offload blocking IO)
            ohlcv = await self._fetch_market_data()
            current_price = float(ohlcv['close'].iloc[-1])
            
            logger.info(f"💹 {self.config.symbol}: ${current_price:.2f}")
            self._log_activity(
                "💹 Market Data Fetched",
                "info",
                {"symbol": self.config.symbol, "price": current_price}
            )
            
            # 2. เช็ค Position
            has_position = await self._check_position()
            
            if has_position:
                self._log_activity("📊 Monitoring Position", "info")
                # 3. Monitor Position (TP/SL/Trailing)
                await self._monitor_position(current_price, ohlcv)
            else:
                self._log_activity("🔍 Searching for Entry Signal", "info")
                # 4. หา Entry Signal
                await self._find_entry(current_price, ohlcv)
        
            # update last check timestamp
            self.last_check_time = datetime.utcnow()

        except Exception as e:
            logger.error(f"Trading cycle error: {e}")
            self._log_activity(f"Trading cycle error: {e}", "error")
    
    async def _fetch_market_data(self) -> pd.DataFrame:
        """ดึงข้อมูลตลาด (OHLCV)"""
        try:
            # ดึงข้อมูล 100 แท่งล่าสุด (run in thread to avoid blocking event loop)
            ohlcv = await asyncio.to_thread(
                self.market_client.fetch_ohlcv,
                self.config.symbol,
                '5m',
                100
            )
            
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        
        except Exception as e:
            logger.error(f"Failed to fetch market data: {e}")
            return pd.DataFrame()
    
    async def _check_position(self) -> bool:
        """เช็คว่ามี Position เปิดอยู่หรือไม่"""
        try:
            # เช็คจาก database
            open_trade = self.db.query(Trade).filter(
                Trade.symbol == self.config.symbol,
                Trade.status == 'open'
            ).first()
            
            if open_trade:
                self.current_position = {
                    'trade_id': open_trade.id,
                    'entry_price': float(open_trade.price),
                    'quantity': float(open_trade.amount),
                    'entry_time': open_trade.timestamp
                }
                return True
            
            self.current_position = None
            return False
        
        except Exception as e:
            logger.error(f"Check position error: {e}")
            return False
    
    async def _monitor_position(self, current_price: float, ohlcv: pd.DataFrame):
        """
        Monitor Position (TP/SL/Trailing Stop)
        """
        if not self.current_position:
            return
        
        entry_price = self.current_position['entry_price']
        pnl_pct = (current_price - entry_price) / entry_price * 100
        
        logger.info(f"📊 Position P/L: {pnl_pct:+.2f}%")
        
        # เรียก AI เพื่อขอ Risk Levels
        # Offload AI analyze if it's synchronous
        analysis = await asyncio.to_thread(
            self.ai_engine.analyze,
            self.config.symbol,
            ohlcv,
            None
        )
        
        tp_pct = analysis.get('take_profit_percent', 1.0)
        sl_pct = analysis.get('stop_loss_percent', 0.5)
        
        # Take Profit
        if pnl_pct >= tp_pct:
            logger.info(f"🎯 Take Profit Triggered: {pnl_pct:.2f}% >= {tp_pct:.2f}%")
            await self._close_position(current_price, "Take Profit")
            return
        
        # Stop Loss
        if pnl_pct <= -sl_pct:
            logger.info(f"🛑 Stop Loss Triggered: {pnl_pct:.2f}% <= -{sl_pct:.2f}%")
            await self._close_position(current_price, "Stop Loss")
            return
        
        # AI SELL Signal
        if analysis.get('action') == 'SELL' and analysis.get('confidence', 0) > 0.7:
            logger.info(f"📉 AI SELL Signal (Confidence: {analysis['confidence']*100:.1f}%)")
            await self._close_position(current_price, "AI Signal")
            return
        
        logger.info(f"✅ Position Hold (waiting for TP/SL)")
    
    async def _find_entry(self, current_price: float, ohlcv: pd.DataFrame):
        """
        หา Entry Signal (BUY)
        
        Pipeline:
        1. Market Regime Filter
        2. On-Chain Filter (Veto Power)
        3. AI Analysis
        4. Execute BUY (ถ้าผ่าน)
        """
        try:
            # 1. On-Chain Filter (Veto Power)
            onchain_analysis = await self.onchain_filter.analyze(self.config.symbol)
            
            if onchain_analysis.veto_buy:
                logger.info(f"🚫 On-Chain VETO: {onchain_analysis.reasoning}")
                return
            
            logger.info(f"✅ On-Chain Status: {onchain_analysis.status}")
            
            # 2. AI Analysis
            analysis = await asyncio.to_thread(
                self.ai_engine.analyze,
                self.config.symbol,
                ohlcv,
                None
            )
            
            action = analysis.get('action', 'HOLD')
            confidence = analysis.get('confidence', 0)
            reason = analysis.get('reason', 'No reason')
            
            logger.info(f"🤖 AI Decision: {action} (Confidence: {confidence*100:.1f}%)")
            logger.info(f"   Reason: {reason}")
            
            # 3. Execute BUY
            if action == 'BUY' and confidence >= self.config.min_confidence:
                await self._open_position(current_price, analysis)
            else:
                logger.info(f"⏸️  No entry signal (waiting...)")
        
        except Exception as e:
            logger.error(f"Find entry error: {e}")
    
    async def _open_position(self, current_price: float, analysis: Dict):
        """
        เปิด Position (BUY)
        """
        try:
            # คำนวณ Quantity จาก Budget
            available_budget = self.config.budget * self.config.position_size_ratio
            quantity = available_budget / current_price
            
            logger.info(f"🛒 Opening Position: {quantity:.6f} {self.config.symbol} @ ${current_price:.2f}")
            self._log_activity(
                "🛒 Opening Position",
                "info",
                {
                    "quantity": round(quantity, 6),
                    "price": current_price,
                    "confidence": analysis.get('confidence', 0) * 100
                }
            )
            
            # ส่งคำสั่ง BUY ไปยัง Binance
            order = await asyncio.to_thread(
                self.trading_client.create_market_buy_order,
                self.config.symbol,
                quantity
            )
            
            # บันทึกใน database
            trade = Trade(
                symbol=self.config.symbol,
                side='BUY',
                amount=quantity,
                price=current_price,
                filled_price=float(order['price']),
                status='open',
                timestamp=datetime.utcnow()
            )
            self.db.add(trade)
            self.db.commit()
            
            logger.info(f"✅ Position Opened: Trade ID {trade.id}")
            self._log_activity(
                "✅ Position Opened",
                "success",
                {
                    "trade_id": trade.id,
                    "entry_price": current_price,
                    "quantity": round(quantity, 6)
                }
            )
            
            # ส่ง Notification
            await self._send_notification(
                f"🛒 BUY EXECUTED\n"
                f"Symbol: {self.config.symbol}\n"
                f"Price: ${current_price:.2f}\n"
                f"Quantity: {quantity:.6f}\n"
                f"Reason: {analysis.get('reason', 'N/A')}"
            )
        
        except Exception as e:
            logger.error(f"Failed to open position: {e}")
            self._log_activity(f"Failed to open position: {e}", "error")
    
    async def _close_position(self, current_price: float, reason: str):
        """
        ปิด Position (SELL)
        """
        try:
            if not self.current_position:
                return
            
            quantity = self.current_position['quantity']
            entry_price = self.current_position['entry_price']
            
            logger.info(f"🔄 Closing Position: {quantity:.6f} {self.config.symbol} @ ${current_price:.2f}")
            
            # Calculate P/L
            pnl = (current_price - entry_price) * quantity
            pnl_pct = (current_price - entry_price) / entry_price * 100
            
            self._log_activity(
                "🔄 Closing Position",
                "info",
                {
                    "reason": reason,
                    "exit_price": current_price,
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct, 2)
                }
            )
            
            # ส่งคำสั่ง SELL ไปยัง Binance
            order = await asyncio.to_thread(
                self.trading_client.create_market_sell_order,
                self.config.symbol,
                quantity
            )
            
            # อัพเดท database
            trade = self.db.query(Trade).filter(
                Trade.id == self.current_position['trade_id']
            ).first()
            
            if trade:
                trade.status = 'completed'
                trade.filled_price = current_price
                self.db.commit()
            
            logger.info(f"✅ Position Closed: P/L = ${pnl:+.2f} ({pnl_pct:+.2f}%)")
            self._log_activity(
                "💰 Position Closed",
                "success" if pnl > 0 else "warning",
                {
                    "pnl": round(pnl, 2),
                    "pnl_pct": round(pnl_pct, 2),
                    "reason": reason
                }
            )
            
            # ส่ง Notification
            await self._send_notification(
                f"💰 SELL EXECUTED\n"
                f"Symbol: {self.config.symbol}\n"
                f"Exit Price: ${current_price:.2f}\n"
                f"P/L: ${pnl:+.2f} ({pnl_pct:+.2f}%)\n"
                f"Reason: {reason}"
            )
            
            # Clear position
            self.current_position = None
        
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            self._log_activity(f"Failed to close position: {e}", "error")
    
    async def _send_notification(self, message: str):
        """
        ส่ง Notification (Telegram/Email/LINE)
        """
        try:
            # TODO: Implement Telegram Bot API
            # TODO: Implement Email notification
            # TODO: Implement LINE Notify
            
            logger.info(f"📱 Notification: {message}")
        
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
