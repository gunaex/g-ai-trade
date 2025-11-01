"""
Event-Driven Backtesting Engine
สำหรับทดสอบกลยุทธ์ AI Trading Bot ด้วยข้อมูลย้อนหลัง
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# EVENT SYSTEM
# ============================================================================

class EventType(Enum):
    MARKET = "MARKET"      # ข้อมูลแท่งเทียนใหม่
    SIGNAL = "SIGNAL"      # สัญญาณจาก AI Strategy
    ORDER = "ORDER"        # คำสั่งซื้อ/ขาย
    FILL = "FILL"          # คำสั่งถูกดำเนินการ


@dataclass
class Event:
    """Base Event Class"""
    timestamp: datetime
    type: EventType = field(init=False)  # ไม่ต้องส่งเข้ามาใน __init__


@dataclass
class MarketEvent(Event):
    """เหตุการณ์ข้อมูลตลาดใหม่"""
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def __post_init__(self):
        self.type = EventType.MARKET


@dataclass
class SignalEvent(Event):
    """สัญญาณจาก AI Strategy"""
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD', 'HALT'
    strength: float   # 0-1 (ความมั่นใจ)
    reason: str       # เหตุผลจาก AI
    
    def __post_init__(self):
        self.type = EventType.SIGNAL


@dataclass
class OrderEvent(Event):
    """คำสั่งซื้อ/ขาย"""
    symbol: str
    order_type: str   # 'MARKET', 'LIMIT'
    direction: str    # 'BUY', 'SELL'
    quantity: float
    price: Optional[float] = None
    
    def __post_init__(self):
        self.type = EventType.ORDER


@dataclass
class FillEvent(Event):
    """คำสั่งที่ถูกดำเนินการแล้ว"""
    symbol: str
    direction: str
    quantity: float
    fill_price: float
    commission: float
    slippage: float
    
    def __post_init__(self):
        self.type = EventType.FILL


# ============================================================================
# DATA HANDLER
# ============================================================================

class HistoricalDataHandler:
    """
    จัดการข้อมูลย้อนหลัง และสร้าง MarketEvent
    """
    
    def __init__(self, symbol: str, data: pd.DataFrame):
        """
        Args:
            symbol: ชื่อคู่เทรด เช่น 'BTCUSDT'
            data: DataFrame with columns [timestamp, open, high, low, close, volume]
        """
        self.symbol = symbol
        self.data = data.sort_values('timestamp').reset_index(drop=True)
        self.current_index = 0
        
        logger.info(f"Loaded {len(self.data)} bars for {symbol}")
    
    def has_next(self) -> bool:
        """เช็คว่ามีข้อมูลแท่งถัดไปหรือไม่"""
        return self.current_index < len(self.data)
    
    def get_next_event(self) -> Optional[MarketEvent]:
        """ดึงข้อมูลแท่งถัดไป"""
        if not self.has_next():
            return None
        
        row = self.data.iloc[self.current_index]
        self.current_index += 1
        
        return MarketEvent(
            timestamp=row['timestamp'],
            symbol=self.symbol,
            open=row['open'],
            high=row['high'],
            low=row['low'],
            close=row['close'],
            volume=row['volume']
        )
    
    def get_latest_bars(self, n: int = 50) -> pd.DataFrame:
        """
        ดึงข้อมูล n แท่งล่าสุด (สำหรับ AI ที่ต้องการ historical context)
        """
        end_idx = self.current_index
        start_idx = max(0, end_idx - n)
        return self.data.iloc[start_idx:end_idx]


# ============================================================================
# AI STRATEGY INTERFACE
# ============================================================================

class AIBacktestStrategy:
    """
    เชื่อมต่อกับ AI Pipeline ที่มีอยู่
    """
    
    def __init__(self, ai_engine, position_tracker=None):
        """
        Args:
            ai_engine: Instance ของ AdvancedAITradingEngine
            position_tracker: ExchangeSimulator instance (เพื่อเช็ค position)
        """
        self.ai_engine = ai_engine
        self.position_tracker = position_tracker
        self.last_signal = None
    
    def calculate_signals_sync(self, event: MarketEvent, historical_bars: pd.DataFrame) -> Optional[SignalEvent]:
        """
        รับ MarketEvent และเรียก AI Pipeline (Synchronous version)
        """
        import asyncio
        import nest_asyncio
        
        try:
            # Get current event loop or create new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Apply nest_asyncio to allow nested event loops
            nest_asyncio.apply()
            
            # Create and run a new task
            coroutine = self._calculate_signals_async(event, historical_bars)
            task = asyncio.ensure_future(coroutine)
            
            # Run until complete and return result
            return loop.run_until_complete(task)
            
        except Exception as e:
            logger.error(f"Strategy error: {e}")
            return None
    
    async def _calculate_signals_async(self, event: MarketEvent, historical_bars: pd.DataFrame) -> Optional[SignalEvent]:
        """
        รับ MarketEvent และเรียก AI Pipeline
        """
        try:
            symbol = event.symbol
            
            # ✅ เช็คว่ามี position อยู่แล้วหรือยัง
            has_position = (self.position_tracker and 
                          symbol in self.position_tracker.positions)
            
            # เรียก AI analysis - analyze() is a regular method, not a coroutine
            analysis = self.ai_engine.analyze(
                symbol=symbol,
                ohlcv=historical_bars,
                order_book=None
            )
            
            # Convert analysis result to standard format
            if isinstance(analysis, dict):
                analysis = analysis  # already a dict
            elif hasattr(analysis, 'to_dict'):
                analysis = analysis.to_dict()
            else:
                try:
                    analysis = dict(analysis)
                except (TypeError, ValueError):
                    analysis = {
                        'action': 'HOLD',
                        'confidence': 0.5,
                        'reason': 'Analysis result could not be converted to dict',
                        'take_profit_percent': 0.5,
                        'stop_loss_percent': 0.3
                    }
            
            action = analysis.get('action', 'HOLD')
            confidence = analysis.get('confidence', 0.5)
            reason = analysis.get('reason', 'No reason provided')
            
            # ✅ ถ้ามี position แล้ว ให้พิจารณาขายเท่านั้น
            if has_position:
                position = self.position_tracker.positions[symbol]
                current_price = event.close
                entry_price = position.entry_price
                
                # คำนวณ % gain/loss
                pnl_pct = (current_price - entry_price) / entry_price * 100
                
                # Take Profit หรือ Stop Loss
                tp_pct = analysis.get('take_profit_percent', 0.5)
                sl_pct = analysis.get('stop_loss_percent', 0.3)
                
                # ถ้ากำไรถึง TP หรือขาดทุนถึง SL
                if pnl_pct >= tp_pct:
                    logger.info(f"🎯 Take Profit triggered: {pnl_pct:.2f}% >= {tp_pct:.2f}%")
                    return SignalEvent(
                        timestamp=event.timestamp,
                        symbol=symbol,
                        signal_type='SELL',
                        strength=0.9,
                        reason=f'Take Profit: {pnl_pct:.2f}%'
                    )
                
                elif pnl_pct <= -sl_pct:
                    logger.info(f"🛑 Stop Loss triggered: {pnl_pct:.2f}% <= -{sl_pct:.2f}%")
                    return SignalEvent(
                        timestamp=event.timestamp,
                        symbol=symbol,
                        signal_type='SELL',
                        strength=0.9,
                        reason=f'Stop Loss: {pnl_pct:.2f}%'
                    )
                
                # ถ้า AI บอก SELL ก็ขาย
                elif action == 'SELL' and confidence > 0.6:
                    logger.info(f"📉 AI SELL signal in position")
                    return SignalEvent(
                        timestamp=event.timestamp,
                        symbol=symbol,
                        signal_type='SELL',
                        strength=confidence,
                        reason=reason
                    )
                
                # ถ้ายังไม่ถึง TP/SL และ AI ไม่บอกขาย ให้ HOLD
                return None
            
            # ✅ ถ้ายังไม่มี position ให้พิจารณาซื้อ
            else:
                if action == 'BUY' and confidence > 0.6:
                    return SignalEvent(
                        timestamp=event.timestamp,
                        symbol=symbol,
                        signal_type='BUY',
                        strength=confidence,
                        reason=reason
                    )
                
                return None
            
        except Exception as e:
            logger.error(f"Strategy error: {e}")
            return None


# ============================================================================
# EXCHANGE SIMULATOR (Brokerage)
# ============================================================================

@dataclass
class Position:
    """ตำแหน่งการถือ"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0


class ExchangeSimulator:
    """
    จำลองการส่งคำสั่งและดำเนินการ
    คำนึงถึง Fees และ Slippage
    """
    
    def __init__(self, 
                 initial_capital: float = 10000,
                 fee_rate: float = 0.001,      # 0.1% fee
                 slippage_rate: float = 0.0005  # 0.05% slippage
                ):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.fee_rate = fee_rate
        self.slippage_rate = slippage_rate
        
        self.positions: Dict[str, Position] = {}
        self.fill_history: List[FillEvent] = []
    
    def execute_order(self, order: OrderEvent, current_price: float) -> Optional[FillEvent]:
        """
        ดำเนินการคำสั่ง (Fill Order)
        """
        # คำนวณ slippage
        if order.direction == 'BUY':
            fill_price = current_price * (1 + self.slippage_rate)
        else:  # SELL
            fill_price = current_price * (1 - self.slippage_rate)
        
        # คำนวณค่า commission
        trade_value = fill_price * order.quantity
        commission = trade_value * self.fee_rate
        
        # ✅ FIX: เช็คว่ามีเงินพอซื้อไหม
        if order.direction == 'BUY':
            # ✅ เช็คว่ามี position อยู่แล้วหรือยัง
            if order.symbol in self.positions:
                logger.warning(f"Already have position in {order.symbol}, skipping BUY")
                return None
            
            total_cost = trade_value + commission
            if total_cost > self.cash:
                logger.warning(f"Insufficient cash: need {total_cost}, have {self.cash}")
                return None
            
            # ดำเนินการซื้อ
            self.cash -= total_cost
            
            # สร้าง Position ใหม่
            self.positions[order.symbol] = Position(
                symbol=order.symbol,
                quantity=order.quantity,
                entry_price=fill_price,
                entry_time=order.timestamp
            )
            
            logger.info(f"✅ BUY: {order.quantity:.6f} {order.symbol} @ ${fill_price:.2f} | Cash: ${self.cash:.2f}")
        
        else:  # SELL
            # เช็คว่ามี Position อยู่หรือไม่
            if order.symbol not in self.positions:
                logger.warning(f"No position to sell: {order.symbol}")
                return None
            
            # ดำเนินการขาย
            position = self.positions.pop(order.symbol)
            proceeds = trade_value - commission
            self.cash += proceeds
            
            # คำนวณ P/L
            pnl = (fill_price - position.entry_price) * position.quantity - commission
            logger.info(f"✅ SELL: {order.quantity:.6f} {order.symbol} @ ${fill_price:.2f} | P/L: ${pnl:.2f} | Cash: ${self.cash:.2f}")
        
        # สร้าง FillEvent
        fill = FillEvent(
            timestamp=order.timestamp,
            symbol=order.symbol,
            direction=order.direction,
            quantity=order.quantity,
            fill_price=fill_price,
            commission=commission,
            slippage=abs(fill_price - current_price)
        )
        
        self.fill_history.append(fill)
        return fill
    
    def update_positions(self, symbol: str, current_price: float):
        """อัพเดท Unrealized P/L"""
        if symbol in self.positions:
            pos = self.positions[symbol]
            pos.unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
    
    def get_total_equity(self, current_prices: Dict[str, float]) -> float:
        """คำนวณ Total Equity (Cash + Positions)"""
        equity = self.cash
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                equity += pos.quantity * current_prices[symbol]
        return equity


# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

class PortfolioManager:
    """
    จัดการพอร์ต และคำนวณ Metrics
    """
    
    def __init__(self, initial_capital: float):
        self.initial_capital = initial_capital
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.trades: List[Dict] = []
        self.current_equity = initial_capital
    
    def update_equity(self, timestamp: datetime, equity: float):
        """บันทึก Equity ณ เวลานั้นๆ"""
        self.equity_curve.append((timestamp, equity))
        self.current_equity = equity
    
    def record_trade(self, fill: FillEvent, pnl: Optional[float] = None):
        """บันทึกการเทรด"""
        self.trades.append({
            'timestamp': fill.timestamp,
            'symbol': fill.symbol,
            'direction': fill.direction,
            'quantity': fill.quantity,
            'price': fill.fill_price,
            'commission': fill.commission,
            'slippage': fill.slippage,
            'pnl': pnl
        })
    
    def get_equity_curve_df(self) -> pd.DataFrame:
        """แปลง Equity Curve เป็น DataFrame"""
        return pd.DataFrame(self.equity_curve, columns=['timestamp', 'equity'])
    
    def calculate_performance_metrics(self) -> Dict:
        """
        คำนวณ Performance Metrics ทั้งหมด
        """
        if len(self.equity_curve) < 2:
            return {}
        
        df = self.get_equity_curve_df()
        df['returns'] = df['equity'].pct_change()
        
        # Total Return
        total_return = (self.current_equity - self.initial_capital) / self.initial_capital * 100
        
        # Max Drawdown (MDD)
        df['cummax'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['cummax']) / df['cummax'] * 100
        max_drawdown = df['drawdown'].min()
        
        # Sharpe Ratio (annualized, assuming 252 trading days)
        mean_return = df['returns'].mean()
        std_return = df['returns'].std()
        sharpe_ratio = (mean_return / std_return) * np.sqrt(252) if std_return > 0 else 0
        
        # Win Rate
        completed_trades = [t for t in self.trades if t.get('pnl') is not None]
        if completed_trades:
            winning_trades = [t for t in completed_trades if t['pnl'] > 0]
            win_rate = len(winning_trades) / len(completed_trades) * 100
            
            # Profit Factor
            total_profit = sum(t['pnl'] for t in completed_trades if t['pnl'] > 0)
            total_loss = abs(sum(t['pnl'] for t in completed_trades if t['pnl'] < 0))
            profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        else:
            win_rate = 0
            profit_factor = 0
        
        # Sortino Ratio (only downside deviation)
        downside_returns = df['returns'][df['returns'] < 0]
        downside_std = downside_returns.std()
        sortino_ratio = (mean_return / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        return {
            'total_return_percent': total_return,
            'max_drawdown_percent': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'win_rate_percent': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(self.trades),
            'completed_rounds': len(completed_trades),
            'final_equity': self.current_equity
        }


# ============================================================================
# MAIN BACKTESTING ENGINE
# ============================================================================

class BacktestingEngine:
    """
    Main Event Loop สำหรับ Backtesting
    """
    
    def __init__(self,
                 symbol: str,
                 data: pd.DataFrame,
                 ai_engine,
                 initial_capital: float = 10000,
                 position_size_percent: float = 0.95  # ใช้เงิน 95% ต่อ trade
                ):
        self.symbol = symbol
        self.data_handler = HistoricalDataHandler(symbol, data)
        self.exchange = ExchangeSimulator(initial_capital)
        
        # ✅ ส่ง exchange เข้าไปใน strategy เพื่อ track position
        self.strategy = AIBacktestStrategy(ai_engine, position_tracker=self.exchange)
        
        self.portfolio = PortfolioManager(initial_capital)
        self.position_size_percent = position_size_percent
        
        self.current_prices = {symbol: 0}
    
    async def run(self):
        """
        Main Event Loop
        """
        logger.info(f"Starting backtest for {self.symbol}")
        
        while self.data_handler.has_next():
            # 1. ดึง Market Event
            market_event = self.data_handler.get_next_event()
            if not market_event:
                break
            
            current_price = market_event.close
            self.current_prices[self.symbol] = current_price
            
            # อัพเดท Unrealized P/L
            self.exchange.update_positions(self.symbol, current_price)
            
            # 2. ส่งข้อมูลให้ Strategy
            historical_bars = self.data_handler.get_latest_bars(n=100)
            signal = self.strategy.calculate_signals_sync(market_event, historical_bars)
            
            # 3. ถ้ามี Signal ให้สร้าง Order
            if signal and signal.signal_type in ['BUY', 'SELL']:
                order = self._generate_order(signal, current_price)
                
                if order:
                    # 4. ส่ง Order ไปยัง Exchange
                    fill = self.exchange.execute_order(order, current_price)
                    
                    if fill:
                        # 5. บันทึกการเทรด
                        pnl = None
                        if fill.direction == 'SELL':
                            # คำนวณ P/L (ถ้าขาย)
                            # (ราคาขาย - ราคาซื้อ) * จำนวน - ค่าธรรมเนียม
                            pnl = 0  # TODO: track this properly
                        
                        self.portfolio.record_trade(fill, pnl)
            
            # 6. อัพเดท Portfolio
            equity = self.exchange.get_total_equity(self.current_prices)
            self.portfolio.update_equity(market_event.timestamp, equity)
        
        logger.info("Backtest completed")
        
        # คำนวณผลลัพธ์
        return self.portfolio.calculate_performance_metrics()
    
    def _generate_order(self, signal: SignalEvent, current_price: float) -> Optional[OrderEvent]:
        """
        สร้าง Order จาก Signal
        """
        if signal.signal_type == 'BUY':
            # ซื้อด้วยเงินที่มี
            available_cash = self.exchange.cash * self.position_size_percent
            quantity = available_cash / current_price
            
            return OrderEvent(
                timestamp=signal.timestamp,
                symbol=signal.symbol,
                order_type='MARKET',
                direction='BUY',
                quantity=quantity
            )
        
        elif signal.signal_type == 'SELL':
            # ขายทั้งหมด
            if signal.symbol in self.exchange.positions:
                position = self.exchange.positions[signal.symbol]
                
                return OrderEvent(
                    timestamp=signal.timestamp,
                    symbol=signal.symbol,
                    order_type='MARKET',
                    direction='SELL',
                    quantity=position.quantity
                )
        
        return None
    
    def generate_tear_sheet(self):
        """
        สร้าง Tear Sheet (รายงานสรุปผล)
        """
        metrics = self.portfolio.calculate_performance_metrics()
        
        print("\n" + "="*60)
        print("BACKTEST TEAR SHEET")
        print("="*60)
        print(f"Symbol: {self.symbol}")
        print(f"Initial Capital: ${self.exchange.initial_capital:,.2f}")
        print(f"Final Equity: ${metrics.get('final_equity', 0):,.2f}")
        print(f"\n{'PERFORMANCE METRICS':^60}")
        print("-"*60)
        print(f"Total Return: {metrics.get('total_return_percent', 0):+.2f}%")
        print(f"Max Drawdown: {metrics.get('max_drawdown_percent', 0):.2f}%")
        print(f"Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Sortino Ratio: {metrics.get('sortino_ratio', 0):.2f}")
        print(f"Win Rate: {metrics.get('win_rate_percent', 0):.1f}%")
        print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        print(f"Total Trades: {metrics.get('total_trades', 0)}")
        print(f"Completed Rounds: {metrics.get('completed_rounds', 0)}")
        print("="*60 + "\n")
        
        return metrics


# ============================================================================
# HELPER: Load Historical Data
# ============================================================================

async def load_historical_data(symbol: str, timeframe: str = '5m', days: int = 30) -> pd.DataFrame:
    """
    ดึงข้อมูลย้อนหลังจาก Binance
    """
    from app.binance_client import get_market_data_client
    import ccxt
    
    try:
        client = get_market_data_client()
        
        # คำนวณเวลา
        since = client.parse8601((datetime.utcnow() - timedelta(days=days)).isoformat())
        
        # ดึงข้อมูล
        ohlcv = client.fetch_ohlcv(symbol, timeframe, since)
        
        # แปลงเป็น DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load historical data: {e}")
        return pd.DataFrame()
