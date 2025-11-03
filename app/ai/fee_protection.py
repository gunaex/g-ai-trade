"""
Fee Protection Module
Prevents excessive trading fees from draining the account
"""
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


class FeeProtectionManager:
    """
    Comprehensive fee protection to prevent overtrading
    
    Features:
    1. Minimum profit threshold (must exceed total fees)
    2. Trade frequency limits (hourly/daily caps)
    3. Minimum hold time enforcement
    4. Fee-adjusted profit calculations
    5. Trade history tracking
    """
    
    def __init__(
        self,
        maker_fee: float = 0.001,  # 0.1% Binance maker fee
        taker_fee: float = 0.001,  # 0.1% Binance taker fee
        min_profit_multiple: float = 3.0,  # Min profit must be 3x total fees
        max_trades_per_hour: int = 2,  # Max 2 trades per hour
        max_trades_per_day: int = 10,  # Max 10 trades per day
        min_hold_time_minutes: int = 30,  # Must hold position for at least 30 minutes
    ):
        """
        Args:
            maker_fee: Maker fee rate (default 0.1% for Binance)
            taker_fee: Taker fee rate (default 0.1% for Binance)
            min_profit_multiple: Minimum profit as multiple of fees (3x = 300%)
            max_trades_per_hour: Maximum trades per hour
            max_trades_per_day: Maximum trades per day
            min_hold_time_minutes: Minimum time to hold position (minutes)
        """
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.min_profit_multiple = min_profit_multiple
        self.max_trades_per_hour = max_trades_per_hour
        self.max_trades_per_day = max_trades_per_day
        self.min_hold_time_minutes = min_hold_time_minutes
        
        # Trade history tracking
        self.trade_history: deque = deque(maxlen=1000)  # Last 1000 trades
        self.position_entry_time: Optional[datetime] = None
        
        logger.info(f"🛡️  Fee Protection Initialized:")
        logger.info(f"   - Trading Fees: {self.maker_fee*100:.2f}% maker, {self.taker_fee*100:.2f}% taker")
        logger.info(f"   - Min Profit: {self.min_profit_multiple}x fees")
        logger.info(f"   - Max Trades: {self.max_trades_per_hour}/hour, {self.max_trades_per_day}/day")
        logger.info(f"   - Min Hold Time: {self.min_hold_time_minutes} minutes")
    
    def calculate_total_fees(
        self,
        entry_price: float,
        exit_price: float,
        position_size_usd: float
    ) -> Dict[str, float]:
        """
        Calculate total fees for a round-trip trade (BUY + SELL)
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            position_size_usd: Position size in USD
            
        Returns:
            Dict with entry_fee, exit_fee, total_fee, fee_pct
        """
        # Entry fee (BUY) - usually taker fee for market orders
        entry_fee = position_size_usd * self.taker_fee
        
        # Exit fee (SELL) - calculate based on exit value
        exit_value = position_size_usd * (exit_price / entry_price)
        exit_fee = exit_value * self.taker_fee
        
        # Total fees
        total_fee = entry_fee + exit_fee
        fee_pct = (total_fee / position_size_usd) * 100
        
        return {
            'entry_fee_usd': entry_fee,
            'exit_fee_usd': exit_fee,
            'total_fee_usd': total_fee,
            'fee_pct': fee_pct
        }
    
    def calculate_net_profit(
        self,
        entry_price: float,
        exit_price: float,
        position_size_usd: float
    ) -> Dict[str, float]:
        """
        Calculate net profit AFTER fees
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            position_size_usd: Position size in USD
            
        Returns:
            Dict with gross_profit, fees, net_profit, net_profit_pct
        """
        # Gross profit (before fees)
        gross_profit = position_size_usd * ((exit_price - entry_price) / entry_price)
        gross_profit_pct = ((exit_price - entry_price) / entry_price) * 100
        
        # Calculate fees
        fees = self.calculate_total_fees(entry_price, exit_price, position_size_usd)
        total_fee = fees['total_fee_usd']
        
        # Net profit (after fees)
        net_profit = gross_profit - total_fee
        net_profit_pct = (net_profit / position_size_usd) * 100
        
        return {
            'gross_profit_usd': gross_profit,
            'gross_profit_pct': gross_profit_pct,
            'total_fee_usd': total_fee,
            'fee_pct': fees['fee_pct'],
            'net_profit_usd': net_profit,
            'net_profit_pct': net_profit_pct
        }
    
    def is_profit_above_fee_threshold(
        self,
        entry_price: float,
        exit_price: float,
        position_size_usd: float
    ) -> Tuple[bool, str]:
        """
        Check if potential profit exceeds minimum threshold (fees × multiple)
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            position_size_usd: Position size in USD
            
        Returns:
            (is_above_threshold, reason)
        """
        profit = self.calculate_net_profit(entry_price, exit_price, position_size_usd)
        
        # Calculate minimum required profit
        min_required_profit = profit['total_fee_usd'] * self.min_profit_multiple
        
        net_profit = profit['net_profit_usd']
        
        if net_profit >= min_required_profit:
            return True, f"✅ Net profit ${net_profit:.2f} exceeds {self.min_profit_multiple}x fees (${min_required_profit:.2f})"
        else:
            return False, f"🚫 Net profit ${net_profit:.2f} below {self.min_profit_multiple}x fees (${min_required_profit:.2f})"
    
    def check_trade_frequency_limits(self) -> Tuple[bool, str]:
        """
        Check if trading frequency is within limits
        
        Returns:
            (is_allowed, reason)
        """
        now = datetime.utcnow()
        
        # Count trades in last hour
        one_hour_ago = now - timedelta(hours=1)
        trades_last_hour = sum(1 for t in self.trade_history if t['timestamp'] >= one_hour_ago)
        
        if trades_last_hour >= self.max_trades_per_hour:
            return False, f"🚫 Trade limit: {trades_last_hour}/{self.max_trades_per_hour} trades in last hour"
        
        # Count trades in last 24 hours
        one_day_ago = now - timedelta(days=1)
        trades_last_day = sum(1 for t in self.trade_history if t['timestamp'] >= one_day_ago)
        
        if trades_last_day >= self.max_trades_per_day:
            return False, f"🚫 Trade limit: {trades_last_day}/{self.max_trades_per_day} trades in last 24h"
        
        return True, f"✅ Trade frequency OK ({trades_last_hour}/hour, {trades_last_day}/day)"
    
    def check_minimum_hold_time(self) -> Tuple[bool, str]:
        """
        Check if position has been held for minimum duration
        
        Returns:
            (is_allowed, reason)
        """
        if self.position_entry_time is None:
            return True, "✅ No open position"
        
        now = datetime.utcnow()
        hold_duration = now - self.position_entry_time
        min_hold_duration = timedelta(minutes=self.min_hold_time_minutes)
        
        if hold_duration < min_hold_duration:
            remaining = (min_hold_duration - hold_duration).total_seconds() / 60
            return False, f"🚫 Must hold for {remaining:.1f} more minutes (min {self.min_hold_time_minutes}m)"
        
        return True, f"✅ Hold time OK ({hold_duration.total_seconds()/60:.1f} minutes)"
    
    def can_open_position(self) -> Tuple[bool, str]:
        """
        Check if we can open a new position (frequency limits)
        
        Returns:
            (is_allowed, reason)
        """
        # Check trade frequency limits
        freq_allowed, freq_reason = self.check_trade_frequency_limits()
        if not freq_allowed:
            return False, freq_reason
        
        return True, "✅ Can open position"
    
    def can_close_position(
        self,
        entry_price: float,
        current_price: float,
        position_size_usd: float,
        force_close: bool = False
    ) -> Tuple[bool, str]:
        """
        Check if we can close position (hold time + profit threshold)
        
        Args:
            entry_price: Entry price
            current_price: Current price
            position_size_usd: Position size in USD
            force_close: Force close (stop loss, etc.) - bypasses profit check
            
        Returns:
            (is_allowed, reason)
        """
        # Check minimum hold time
        hold_allowed, hold_reason = self.check_minimum_hold_time()
        if not hold_allowed and not force_close:
            return False, hold_reason
        
        # For force close (stop loss), allow regardless of profit
        if force_close:
            return True, "✅ Force close (stop loss/emergency)"
        
        # Check if profit exceeds fee threshold
        profit_allowed, profit_reason = self.is_profit_above_fee_threshold(
            entry_price, current_price, position_size_usd
        )
        
        if not profit_allowed:
            return False, profit_reason
        
        return True, f"✅ Can close position | {profit_reason}"
    
    def record_trade(
        self,
        trade_type: str,
        price: float,
        position_size_usd: float,
        profit_usd: Optional[float] = None
    ):
        """
        Record a trade in history
        
        Args:
            trade_type: 'BUY' or 'SELL'
            price: Trade price
            position_size_usd: Position size in USD
            profit_usd: Profit for SELL trades (optional)
        """
        trade_record = {
            'timestamp': datetime.utcnow(),
            'type': trade_type,
            'price': price,
            'position_size_usd': position_size_usd,
            'profit_usd': profit_usd
        }
        
        self.trade_history.append(trade_record)
        
        # Update position entry time
        if trade_type == 'BUY':
            self.position_entry_time = datetime.utcnow()
            logger.info(f"📝 Recorded BUY: ${price:.2f} | Position: ${position_size_usd:.2f}")
        elif trade_type == 'SELL':
            self.position_entry_time = None
            logger.info(f"📝 Recorded SELL: ${price:.2f} | Profit: ${profit_usd:.2f}")
    
    def get_fee_summary(self) -> Dict:
        """
        Get summary of fees paid over time
        
        Returns:
            Dict with fee statistics
        """
        now = datetime.utcnow()
        
        # Calculate fees for last 24 hours
        one_day_ago = now - timedelta(days=1)
        recent_trades = [t for t in self.trade_history if t['timestamp'] >= one_day_ago]
        
        # Estimate fees (0.1% per trade)
        total_volume_24h = sum(t['position_size_usd'] for t in recent_trades)
        total_fees_24h = total_volume_24h * (self.taker_fee + self.maker_fee)
        
        # Count trades
        trades_24h = len(recent_trades)
        buy_trades = sum(1 for t in recent_trades if t['type'] == 'BUY')
        sell_trades = sum(1 for t in recent_trades if t['type'] == 'SELL')
        
        # Calculate total profit
        total_profit_24h = sum(t.get('profit_usd', 0) for t in recent_trades if t['type'] == 'SELL')
        
        return {
            'trades_24h': trades_24h,
            'buy_trades_24h': buy_trades,
            'sell_trades_24h': sell_trades,
            'volume_24h_usd': total_volume_24h,
            'fees_24h_usd': total_fees_24h,
            'profit_24h_usd': total_profit_24h,
            'net_profit_24h_usd': total_profit_24h - total_fees_24h,
            'fee_to_profit_ratio': (total_fees_24h / total_profit_24h * 100) if total_profit_24h > 0 else 0
        }
    
    def get_breakeven_price(
        self,
        entry_price: float,
        position_size_usd: float
    ) -> Dict[str, float]:
        """
        Calculate breakeven price (price needed to cover fees)
        
        Args:
            entry_price: Entry price
            position_size_usd: Position size in USD
            
        Returns:
            Dict with breakeven_price, breakeven_pct, min_profitable_price
        """
        # Total fee rate (both entry and exit)
        total_fee_rate = self.taker_fee + self.taker_fee  # 0.2% total
        
        # Breakeven price (just covers fees)
        breakeven_price = entry_price * (1 + total_fee_rate)
        breakeven_pct = total_fee_rate * 100
        
        # Minimum profitable price (fees × multiple)
        min_profitable_price = entry_price * (1 + total_fee_rate * self.min_profit_multiple)
        min_profitable_pct = (total_fee_rate * self.min_profit_multiple) * 100
        
        return {
            'breakeven_price': breakeven_price,
            'breakeven_pct': breakeven_pct,
            'min_profitable_price': min_profitable_price,
            'min_profitable_pct': min_profitable_pct,
            'entry_price': entry_price
        }
