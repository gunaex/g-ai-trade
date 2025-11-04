"""
Paper Trading Engine - Simulates trading without real money

This module provides a complete paper trading system that:
- Tracks virtual balance and positions
- Simulates order execution with realistic fills
- Calculates fees, slippage, and P&L
- Maintains trade history for analysis
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json


class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class PaperOrder:
    """Represents a simulated order"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_at: Optional[datetime] = None
    fee: float = 0.0
    fee_asset: str = "USDT"


@dataclass
class PaperPosition:
    """Represents current holdings"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    total_cost: float
    fees_paid: float = 0.0


@dataclass
class PaperBalance:
    """Virtual account balance"""
    usdt: float = 10000.0  # Starting balance
    base_asset: float = 0.0  # e.g., BTC, BNB, ETH
    locked_usdt: float = 0.0
    locked_base: float = 0.0


@dataclass
class TradeResult:
    """Result of a completed trade (buy + sell)"""
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    entry_time: datetime
    exit_time: datetime
    gross_pnl: float
    fees: float
    net_pnl: float
    pnl_percent: float
    holding_duration: float  # minutes


class PaperTradingEngine:
    """
    Simulates trading with virtual money
    
    Features:
    - Realistic order fills based on current market price
    - Configurable slippage simulation
    - Fee calculation (maker/taker)
    - Position tracking
    - Trade history
    - Performance metrics
    """
    
    def __init__(
        self,
        initial_balance: float = 10000.0,
        maker_fee: float = 0.001,  # 0.1% Binance TH maker
        taker_fee: float = 0.001,  # 0.1% Binance TH taker
        slippage_bps: float = 5.0,  # 5 basis points = 0.05%
    ):
        self.balance = PaperBalance(usdt=initial_balance)
        self.initial_balance = initial_balance
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.slippage_bps = slippage_bps
        
        self.current_position: Optional[PaperPosition] = None
        self.orders: List[PaperOrder] = []
        self.trade_history: List[TradeResult] = []
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_fees_paid = 0.0
        self.peak_balance = initial_balance
        self.max_drawdown = 0.0
    
    def get_available_balance(self, asset: str = "USDT") -> float:
        """Get available (unlocked) balance"""
        if asset == "USDT":
            return self.balance.usdt - self.balance.locked_usdt
        return self.balance.base_asset - self.balance.locked_base
    
    def get_total_value(self, current_price: float) -> float:
        """Calculate total account value in USDT"""
        usdt_value = self.balance.usdt
        base_value = self.balance.base_asset * current_price
        return usdt_value + base_value
    
    def simulate_slippage(self, price: float, side: OrderSide) -> float:
        """
        Simulate realistic slippage
        BUY: slightly higher price (worse fill)
        SELL: slightly lower price (worse fill)
        """
        slippage_factor = self.slippage_bps / 10000.0  # Convert basis points
        if side == OrderSide.BUY:
            return price * (1 + slippage_factor)
        else:
            return price * (1 - slippage_factor)
    
    def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        current_price: float,
        use_taker_fee: bool = True
    ) -> Tuple[bool, Optional[PaperOrder], str]:
        """
        Simulate a market order
        
        Returns:
            (success, order, message)
        """
        # Simulate realistic fill price with slippage
        fill_price = self.simulate_slippage(current_price, side)
        
        # Calculate fee
        fee_rate = self.taker_fee if use_taker_fee else self.maker_fee
        
        order_id = f"PAPER_{datetime.now(timezone.utc).timestamp()}"
        order = PaperOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=current_price,
            timestamp=datetime.now(timezone.utc),
        )
        
        # Validate and execute
        if side == OrderSide.BUY:
            cost = quantity * fill_price
            fee = cost * fee_rate
            total_cost = cost + fee
            
            if total_cost > self.get_available_balance("USDT"):
                order.status = OrderStatus.REJECTED
                self.orders.append(order)
                return False, order, f"Insufficient USDT balance. Need {total_cost:.2f}, have {self.get_available_balance('USDT'):.2f}"
            
            # Execute buy
            self.balance.usdt -= total_cost
            self.balance.base_asset += quantity
            self.total_fees_paid += fee
            
            order.status = OrderStatus.FILLED
            order.filled_price = fill_price
            order.filled_at = datetime.now(timezone.utc)
            order.fee = fee
            
            # Create position
            self.current_position = PaperPosition(
                symbol=symbol,
                quantity=quantity,
                entry_price=fill_price,
                entry_time=datetime.now(timezone.utc),
                total_cost=cost,
                fees_paid=fee
            )
            
        else:  # SELL
            if quantity > self.get_available_balance("BASE"):
                order.status = OrderStatus.REJECTED
                self.orders.append(order)
                return False, order, f"Insufficient {symbol.split('/')[0]} balance"
            
            # Execute sell
            revenue = quantity * fill_price
            fee = revenue * fee_rate
            net_revenue = revenue - fee
            
            self.balance.base_asset -= quantity
            self.balance.usdt += net_revenue
            self.total_fees_paid += fee
            
            order.status = OrderStatus.FILLED
            order.filled_price = fill_price
            order.filled_at = datetime.now(timezone.utc)
            order.fee = fee
            
            # Record trade result if we had a position
            if self.current_position:
                self._record_trade(fill_price, fee)
                self.current_position = None
        
        self.orders.append(order)
        self._update_metrics()
        
        return True, order, "Order filled successfully"
    
    def _record_trade(self, exit_price: float, exit_fee: float):
        """Record a completed trade (buy -> sell)"""
        if not self.current_position:
            return
        
        pos = self.current_position
        exit_time = datetime.now(timezone.utc)
        
        # Calculate P&L
        gross_pnl = (exit_price - pos.entry_price) * pos.quantity
        total_fees = pos.fees_paid + exit_fee
        net_pnl = gross_pnl - total_fees
        pnl_percent = (net_pnl / pos.total_cost) * 100
        
        holding_duration = (exit_time - pos.entry_time).total_seconds() / 60
        
        result = TradeResult(
            symbol=pos.symbol,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            quantity=pos.quantity,
            entry_time=pos.entry_time,
            exit_time=exit_time,
            gross_pnl=gross_pnl,
            fees=total_fees,
            net_pnl=net_pnl,
            pnl_percent=pnl_percent,
            holding_duration=holding_duration
        )
        
        self.trade_history.append(result)
        self.total_trades += 1
        
        if net_pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
    
    def _update_metrics(self):
        """Update performance metrics"""
        # Track peak and drawdown
        current_value = self.balance.usdt + self.balance.base_asset
        if current_value > self.peak_balance:
            self.peak_balance = current_value
        
        drawdown = ((self.peak_balance - current_value) / self.peak_balance) * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def get_performance_summary(self, current_price: float = 0) -> Dict:
        """Get comprehensive performance metrics"""
        total_value = self.get_total_value(current_price) if current_price > 0 else self.balance.usdt
        total_pnl = total_value - self.initial_balance
        roi = (total_pnl / self.initial_balance) * 100
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        avg_win = 0
        avg_loss = 0
        if self.trade_history:
            wins = [t.net_pnl for t in self.trade_history if t.net_pnl > 0]
            losses = [t.net_pnl for t in self.trade_history if t.net_pnl <= 0]
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return {
            "initial_balance": self.initial_balance,
            "current_balance_usdt": self.balance.usdt,
            "current_balance_base": self.balance.base_asset,
            "total_value": total_value,
            "total_pnl": total_pnl,
            "roi_percent": roi,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": win_rate,
            "total_fees_paid": self.total_fees_paid,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "max_drawdown": self.max_drawdown,
            "has_open_position": self.current_position is not None,
        }
    
    def export_report(self, filepath: str = "paper_trading_report.json"):
        """Export detailed trading report"""
        report = {
            "summary": self.get_performance_summary(),
            "trades": [
                {
                    "symbol": t.symbol,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "quantity": t.quantity,
                    "entry_time": t.entry_time.isoformat(),
                    "exit_time": t.exit_time.isoformat(),
                    "gross_pnl": t.gross_pnl,
                    "fees": t.fees,
                    "net_pnl": t.net_pnl,
                    "pnl_percent": t.pnl_percent,
                    "holding_minutes": t.holding_duration,
                }
                for t in self.trade_history
            ],
            "orders": [
                {
                    "order_id": o.order_id,
                    "symbol": o.symbol,
                    "side": o.side.value,
                    "quantity": o.quantity,
                    "price": o.price,
                    "status": o.status.value,
                    "filled_price": o.filled_price,
                    "fee": o.fee,
                    "timestamp": o.timestamp.isoformat(),
                }
                for o in self.orders
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
