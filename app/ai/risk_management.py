"""
Advanced Risk Management Module
- Kelly Criterion Position Sizing
- Adaptive Trailing Stop Loss
- Performance Tracking
- Portfolio Risk Management
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Dynamic position sizing using Kelly Criterion and volatility adjustment
    Prevents over-leverage and adapts to market conditions
    """
    
    def __init__(self, max_risk_per_trade: float = 0.02):
        """
        Args:
            max_risk_per_trade: Maximum % of account to risk per trade (default 2%)
        """
        self.max_risk_per_trade = max_risk_per_trade
        
    def calculate_position_size(
        self,
        account_balance: float,
        win_rate: float,
        avg_win_pct: float,
        avg_loss_pct: float,
        current_volatility: float,
        confidence: float = 1.0
    ) -> Dict[str, float]:
        """
        Calculate optimal position size using Kelly Criterion with safety adjustments
        
        Args:
            account_balance: Total account value in USD
            win_rate: Historical win rate (0-1)
            avg_win_pct: Average winning trade % (e.g., 0.05 for 5%)
            avg_loss_pct: Average losing trade % (e.g., 0.03 for 3%)
            current_volatility: Current market volatility (std dev of returns)
            confidence: AI confidence score (0-1) - reduces size for uncertain trades
            
        Returns:
            Dict with position_size_usd, position_pct, kelly_fraction, adjustments
        """
        try:
            # Validate inputs
            if account_balance <= 0:
                logger.warning("Invalid account balance")
                return self._minimum_position(account_balance)
            
            if avg_loss_pct == 0:
                avg_loss_pct = 0.02  # Default 2% loss
            
            # Calculate Kelly Criterion: f* = (p*b - q) / b
            # where p = win rate, q = lose rate, b = win/loss ratio
            b = avg_win_pct / avg_loss_pct if avg_loss_pct > 0 else 2.0
            kelly_fraction = (win_rate * b - (1 - win_rate)) / b
            
            # Apply Half-Kelly for safety (reduce aggressive sizing)
            half_kelly = kelly_fraction / 2
            
            # Cap maximum Kelly at 25% to prevent over-leverage
            safe_kelly = max(0, min(0.25, half_kelly))
            
            # Volatility adjustment - reduce size in high volatility
            # If volatility is 2x normal (0.04 vs 0.02), reduce size by ~33%
            baseline_volatility = 0.02  # 2% daily volatility baseline
            volatility_multiplier = baseline_volatility / max(current_volatility, 0.01)
            volatility_multiplier = min(1.0, max(0.3, volatility_multiplier))  # Cap 0.3-1.0
            
            # Confidence adjustment - reduce size for low confidence trades
            confidence_multiplier = max(0.5, confidence)  # Min 50% size even at low confidence
            
            # Combined position sizing
            position_fraction = safe_kelly * volatility_multiplier * confidence_multiplier
            
            # Apply maximum risk limit
            position_fraction = min(position_fraction, self.max_risk_per_trade)
            
            # Calculate position size in USD
            position_size_usd = account_balance * position_fraction
            
            # Ensure minimum position (0.5% of account)
            min_position = account_balance * 0.005
            position_size_usd = max(min_position, position_size_usd)
            
            logger.info(f"💰 Position Sizing: ${position_size_usd:.2f} ({position_fraction*100:.2f}% of account)")
            logger.info(f"   Kelly: {safe_kelly*100:.1f}%, Vol Adj: {volatility_multiplier:.2f}, Conf Adj: {confidence_multiplier:.2f}")
            
            return {
                'position_size_usd': position_size_usd,
                'position_pct': position_fraction * 100,
                'kelly_fraction': safe_kelly,
                'volatility_multiplier': volatility_multiplier,
                'confidence_multiplier': confidence_multiplier,
                'adjustments': {
                    'kelly_raw': kelly_fraction,
                    'kelly_safe': safe_kelly,
                    'after_volatility': safe_kelly * volatility_multiplier,
                    'final': position_fraction
                }
            }
            
        except Exception as e:
            logger.error(f"Position sizing error: {e}", exc_info=True)
            return self._minimum_position(account_balance)
    
    def _minimum_position(self, account_balance: float) -> Dict[str, float]:
        """Fallback to minimum safe position"""
        min_size = account_balance * 0.005  # 0.5% minimum
        return {
            'position_size_usd': min_size,
            'position_pct': 0.5,
            'kelly_fraction': 0.005,
            'volatility_multiplier': 1.0,
            'confidence_multiplier': 1.0,
            'adjustments': {'kelly_raw': 0.005, 'kelly_safe': 0.005, 'after_volatility': 0.005, 'final': 0.005}
        }


class AdaptiveStopLoss:
    """
    Dynamic trailing stop loss that adapts to:
    - Market volatility (ATR)
    - Support/Resistance levels (swing lows/highs)
    - Trend strength
    """
    
    def __init__(self, entry_price: float, side: str, atr_multiplier: float = 2.5):
        """
        Args:
            entry_price: Entry price of the position
            side: 'BUY' or 'SELL'
            atr_multiplier: Multiplier for ATR-based stop (default 2.5)
        """
        self.entry_price = entry_price
        self.side = side.upper()
        self.atr_multiplier = atr_multiplier
        
        # Track extreme price for trailing
        self.extreme_price = entry_price  # Highest for BUY, Lowest for SELL
        self.current_stop = None
        
    def calculate_atr(self, ohlcv: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        try:
            high = ohlcv['high']
            low = ohlcv['low']
            close = ohlcv['close']
            
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            atr_value = atr.iloc[-1]
            if pd.isna(atr_value) or np.isnan(atr_value):
                # Fallback: use price range
                return (ohlcv['high'].tail(period).max() - ohlcv['low'].tail(period).min()) / period
            
            return float(atr_value)
            
        except Exception as e:
            logger.warning(f"ATR calculation failed: {e}")
            return ohlcv['close'].iloc[-1] * 0.01  # 1% of price as fallback
    
    def find_swing_level(self, ohlcv: pd.DataFrame, lookback: int = 10) -> float:
        """Find recent swing low (for BUY) or swing high (for SELL)"""
        try:
            if self.side == 'BUY':
                # Find swing low (support level)
                swing_level = ohlcv['low'].rolling(window=lookback).min().iloc[-1]
            else:  # SELL
                # Find swing high (resistance level)
                swing_level = ohlcv['high'].rolling(window=lookback).max().iloc[-1]
            
            return float(swing_level) if not pd.isna(swing_level) else self.entry_price
            
        except Exception as e:
            logger.warning(f"Swing level calculation failed: {e}")
            return self.entry_price
    
    def update_stop(self, ohlcv: pd.DataFrame, current_price: float) -> Dict[str, float]:
        """
        Update trailing stop loss
        
        Returns:
            Dict with stop_loss_price, stop_distance_pct, method_used
        """
        try:
            # Update extreme price (for trailing)
            if self.side == 'BUY':
                self.extreme_price = max(self.extreme_price, current_price)
            else:  # SELL
                self.extreme_price = min(self.extreme_price, current_price)
            
            # Calculate ATR
            atr = self.calculate_atr(ohlcv)
            
            # Find swing level (support/resistance)
            swing_level = self.find_swing_level(ohlcv)
            
            # Method 1: ATR-based trailing stop
            if self.side == 'BUY':
                atr_stop = self.extreme_price - (atr * self.atr_multiplier)
            else:  # SELL
                atr_stop = self.extreme_price + (atr * self.atr_multiplier)
            
            # Method 2: Swing-based stop (just beyond support/resistance)
            if self.side == 'BUY':
                swing_stop = swing_level * 0.998  # Just below swing low
            else:  # SELL
                swing_stop = swing_level * 1.002  # Just above swing high
            
            # Method 3: Minimum stop (never worse than -3% from entry)
            if self.side == 'BUY':
                min_stop = self.entry_price * 0.97
            else:  # SELL
                min_stop = self.entry_price * 1.03
            
            # Choose best stop (tightest for BUY, loosest for SELL that still protects)
            if self.side == 'BUY':
                # For BUY: want highest stop (closest to price, tightest)
                self.current_stop = max(atr_stop, swing_stop, min_stop)
                method = 'ATR' if self.current_stop == atr_stop else 'SWING' if self.current_stop == swing_stop else 'MIN'
            else:  # SELL
                # For SELL: want lowest stop (closest to price, tightest)
                self.current_stop = min(atr_stop, swing_stop, min_stop)
                method = 'ATR' if self.current_stop == atr_stop else 'SWING' if self.current_stop == swing_stop else 'MIN'
            
            # Calculate stop distance
            if self.side == 'BUY':
                stop_distance_pct = ((current_price - self.current_stop) / current_price) * 100
            else:  # SELL
                stop_distance_pct = ((self.current_stop - current_price) / current_price) * 100
            
            logger.debug(f"🛡️  Stop Loss Updated: ${self.current_stop:.2f} ({stop_distance_pct:.2f}% away) - Method: {method}")
            
            return {
                'stop_loss_price': self.current_stop,
                'stop_distance_pct': stop_distance_pct,
                'method_used': method,
                'atr': atr,
                'swing_level': swing_level,
                'extreme_price': self.extreme_price,
                'calculations': {
                    'atr_stop': atr_stop,
                    'swing_stop': swing_stop,
                    'min_stop': min_stop
                }
            }
            
        except Exception as e:
            logger.error(f"Stop loss update error: {e}", exc_info=True)
            # Fallback to simple percentage stop
            if self.side == 'BUY':
                fallback_stop = current_price * 0.97
            else:
                fallback_stop = current_price * 1.03
            
            return {
                'stop_loss_price': fallback_stop,
                'stop_distance_pct': 3.0,
                'method_used': 'FALLBACK',
                'atr': 0,
                'swing_level': current_price,
                'extreme_price': current_price
            }
    
    def should_exit(self, current_price: float) -> Tuple[bool, str]:
        """
        Check if stop loss triggered
        
        Returns:
            Tuple of (should_exit: bool, reason: str)
        """
        if self.current_stop is None:
            return False, ""
        
        if self.side == 'BUY':
            if current_price <= self.current_stop:
                return True, f"Stop Loss Hit: ${current_price:.2f} <= ${self.current_stop:.2f}"
        else:  # SELL
            if current_price >= self.current_stop:
                return True, f"Stop Loss Hit: ${current_price:.2f} >= ${self.current_stop:.2f}"
        
        return False, ""


class PerformanceTracker:
    """
    Track trading performance and calculate statistics
    Enables continuous improvement through data-driven insights
    """
    
    def __init__(self):
        self.trades: List[Dict] = []
        
    def log_trade(self, trade: Dict):
        """
        Record a completed trade
        
        Expected fields:
            - timestamp: datetime
            - symbol: str
            - side: 'BUY' or 'SELL'
            - entry_price: float
            - exit_price: float
            - quantity: float
            - pnl_usd: float
            - pnl_pct: float
            - confidence: float (0-1)
            - regime: str
            - hold_time_minutes: float
        """
        trade['timestamp'] = trade.get('timestamp', datetime.now())
        self.trades.append(trade)
        
        logger.info(f"📝 Trade Logged: {trade['symbol']} {trade['side']} PnL: ${trade['pnl_usd']:+.2f} ({trade['pnl_pct']:+.2f}%)")
    
    def get_statistics(self, lookback_days: int = 30) -> Dict:
        """
        Calculate comprehensive trading statistics
        
        Returns:
            Dict with win_rate, avg_win, avg_loss, profit_factor, sharpe_ratio, etc.
        """
        try:
            # Filter recent trades
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            recent_trades = [t for t in self.trades if t['timestamp'] > cutoff_date]
            
            if not recent_trades:
                return self._empty_stats()
            
            # Separate wins and losses
            wins = [t for t in recent_trades if t['pnl_usd'] > 0]
            losses = [t for t in recent_trades if t['pnl_usd'] < 0]
            breakeven = [t for t in recent_trades if t['pnl_usd'] == 0]
            
            total_trades = len(recent_trades)
            win_count = len(wins)
            loss_count = len(losses)
            
            # Win Rate
            win_rate = win_count / total_trades if total_trades > 0 else 0
            
            # Average Win/Loss (in %)
            avg_win_pct = np.mean([t['pnl_pct'] for t in wins]) if wins else 0
            avg_loss_pct = abs(np.mean([t['pnl_pct'] for t in losses])) if losses else 0
            
            # Profit Factor: (total wins) / (total losses)
            total_win_usd = sum(t['pnl_usd'] for t in wins)
            total_loss_usd = abs(sum(t['pnl_usd'] for t in losses))
            profit_factor = total_win_usd / total_loss_usd if total_loss_usd > 0 else float('inf')
            
            # Net PnL
            net_pnl_usd = sum(t['pnl_usd'] for t in recent_trades)
            
            # Sharpe Ratio (risk-adjusted returns)
            returns = [t['pnl_pct'] for t in recent_trades]
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (avg_return / std_return * np.sqrt(365)) if std_return > 0 else 0
            
            # Maximum Drawdown
            max_drawdown_pct = self._calculate_max_drawdown(recent_trades)
            
            # Average holding time
            avg_hold_time_minutes = np.mean([t.get('hold_time_minutes', 0) for t in recent_trades])
            
            # Expectancy: (Win Rate * Avg Win) - (Loss Rate * Avg Loss)
            expectancy = (win_rate * avg_win_pct) - ((1 - win_rate) * avg_loss_pct)
            
            # Largest win and loss
            largest_win_pct = max([t['pnl_pct'] for t in wins]) if wins else 0
            largest_loss_pct = min([t['pnl_pct'] for t in losses]) if losses else 0
            
            stats = {
                'total_trades': total_trades,
                'win_count': win_count,
                'loss_count': loss_count,
                'breakeven_count': len(breakeven),
                'win_rate': round(win_rate, 4),
                'avg_win_pct': round(avg_win_pct, 4),
                'avg_loss_pct': round(avg_loss_pct, 4),
                'profit_factor': round(profit_factor, 2),
                'expectancy_pct': round(expectancy, 4),
                'net_pnl_usd': round(net_pnl_usd, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown_pct': round(max_drawdown_pct, 2),
                'largest_win_pct': round(largest_win_pct, 2),
                'largest_loss_pct': round(largest_loss_pct, 2),
                'avg_hold_time_minutes': round(avg_hold_time_minutes, 1),
                'lookback_days': lookback_days
            }
            
            logger.info(f"📊 Performance Stats ({lookback_days}d): WR={win_rate*100:.1f}%, PF={profit_factor:.2f}, Sharpe={sharpe_ratio:.2f}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Performance statistics error: {e}", exc_info=True)
            return self._empty_stats()
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """
        Calculate maximum peak-to-trough decline in %
        """
        try:
            cumulative_returns = [0]
            for t in trades:
                cumulative_returns.append(cumulative_returns[-1] + t['pnl_pct'])
            
            peak = cumulative_returns[0]
            max_dd = 0
            
            for value in cumulative_returns:
                if value > peak:
                    peak = value
                dd = (peak - value)
                max_dd = max(max_dd, dd)
            
            return max_dd
            
        except Exception as e:
            logger.warning(f"Max drawdown calculation error: {e}")
            return 0.0
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics structure"""
        return {
            'total_trades': 0,
            'win_count': 0,
            'loss_count': 0,
            'breakeven_count': 0,
            'win_rate': 0.5,
            'avg_win_pct': 0.0,
            'avg_loss_pct': 0.0,
            'profit_factor': 0.0,
            'expectancy_pct': 0.0,
            'net_pnl_usd': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown_pct': 0.0,
            'largest_win_pct': 0.0,
            'largest_loss_pct': 0.0,
            'avg_hold_time_minutes': 0.0,
            'lookback_days': 30
        }
    
    def get_recent_trades(self, limit: int = 10) -> List[Dict]:
        """Get most recent trades"""
        return sorted(self.trades, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_trade_count(self) -> int:
        """Get total number of trades"""
        return len(self.trades)
