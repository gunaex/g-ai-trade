"""
Advanced Market Analysis Module
- Multi-Timeframe Analysis
- Volume Profile Analysis (replaces fake sentiment)
- Order Book Liquidity Analysis
- Correlation Analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MultiTimeframeAnalyzer:
    """
    Analyze market across multiple timeframes for trend confluence
    Only take trades when multiple timeframes align
    """
    
    def __init__(self, market_client):
        """
        Args:
            market_client: ccxt exchange client for fetching data
        """
        self.market_client = market_client
        self.timeframes = ['5m', '15m', '1h', '4h', '1d']
        self.weights = {
            '5m': 0.10,   # Short-term noise
            '15m': 0.15,  # Entry timing
            '1h': 0.25,   # Primary trading TF
            '4h': 0.25,   # Trend confirmation
            '1d': 0.25    # Major trend
        }
    
    def analyze(self, symbol: str) -> Dict:
        """
        Analyze trend direction across all timeframes
        
        Returns:
            Dict with alignment score, signals per timeframe, and recommendation
        """
        try:
            signals = []
            
            for tf in self.timeframes:
                try:
                    # Fetch OHLCV data
                    ohlcv = self.market_client.fetch_ohlcv(symbol, tf, limit=100)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # Analyze this timeframe
                    tf_signal = self._analyze_timeframe(df, tf)
                    signals.append(tf_signal)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze {tf} for {symbol}: {e}")
                    # Add neutral signal for failed timeframe
                    signals.append({
                        'timeframe': tf,
                        'trend': 'NEUTRAL',
                        'strength': 0.5,
                        'weight': self.weights.get(tf, 0.2),
                        'emas': {'aligned': False}
                    })
            
            # Calculate weighted alignment score
            bullish_score = sum(
                s['weight'] * s['strength'] 
                for s in signals 
                if s['trend'] == 'BULLISH'
            )
            
            bearish_score = sum(
                s['weight'] * (1 - s['strength']) 
                for s in signals 
                if s['trend'] == 'BEARISH'
            )
            
            neutral_weight = sum(
                s['weight'] 
                for s in signals 
                if s['trend'] == 'NEUTRAL'
            )
            
            # Determine overall alignment
            total_bullish = bullish_score / (1 - neutral_weight) if neutral_weight < 1 else 0
            total_bearish = bearish_score / (1 - neutral_weight) if neutral_weight < 1 else 0
            
            # Classification
            if total_bullish > 0.7:
                alignment = 'STRONG_BULLISH'
                action = 'BUY'
                confidence = total_bullish
            elif total_bullish > 0.5:
                alignment = 'WEAK_BULLISH'
                action = 'BUY'
                confidence = total_bullish * 0.8  # Reduce confidence for weak signals
            elif total_bearish > 0.7:
                alignment = 'STRONG_BEARISH'
                action = 'SELL'
                confidence = total_bearish
            elif total_bearish > 0.5:
                alignment = 'WEAK_BEARISH'
                action = 'SELL'
                confidence = total_bearish * 0.8
            else:
                alignment = 'MIXED'
                action = 'HOLD'
                confidence = 0.5
            
            result = {
                'alignment': alignment,
                'action': action,
                'confidence': confidence,
                'bullish_score': bullish_score,
                'bearish_score': bearish_score,
                'signals': signals,
                'timeframes_analyzed': len([s for s in signals if s['trend'] != 'NEUTRAL'])
            }
            
            logger.info(f"📈 Multi-TF Analysis: {alignment} (Confidence: {confidence*100:.1f}%)")
            logger.debug(f"   Bullish: {bullish_score:.2f}, Bearish: {bearish_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Multi-timeframe analysis error: {e}", exc_info=True)
            return {
                'alignment': 'UNKNOWN',
                'action': 'HOLD',
                'confidence': 0.0,
                'bullish_score': 0.0,
                'bearish_score': 0.0,
                'signals': [],
                'error': str(e)
            }
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """
        Analyze single timeframe using EMA alignment
        
        Strategy: Triple EMA (9, 21, 50)
        - Bullish: EMA9 > EMA21 > EMA50 and price > EMA9
        - Bearish: EMA9 < EMA21 < EMA50 and price < EMA9
        """
        try:
            # Calculate EMAs
            ema_9 = df['close'].ewm(span=9, adjust=False).mean()
            ema_21 = df['close'].ewm(span=21, adjust=False).mean()
            ema_50 = df['close'].ewm(span=50, adjust=False).mean()
            
            current_price = df['close'].iloc[-1]
            current_ema9 = ema_9.iloc[-1]
            current_ema21 = ema_21.iloc[-1]
            current_ema50 = ema_50.iloc[-1]
            
            # Check EMA alignment
            bullish_alignment = (current_ema9 > current_ema21 > current_ema50 and 
                                current_price > current_ema9)
            
            bearish_alignment = (current_ema9 < current_ema21 < current_ema50 and 
                                current_price < current_ema9)
            
            # Calculate trend strength (distance between EMAs)
            ema_spread = abs(current_ema9 - current_ema50) / current_price
            strength = min(1.0, ema_spread * 50)  # Normalize to 0-1
            
            # Price momentum
            price_change = (current_price - df['close'].iloc[-10]) / df['close'].iloc[-10]
            momentum_strength = abs(price_change) * 10  # Amplify for scoring
            
            # Combined strength
            combined_strength = min(1.0, (strength + momentum_strength) / 2)
            
            if bullish_alignment:
                trend = 'BULLISH'
                trend_strength = 0.5 + (combined_strength / 2)  # 0.5-1.0 range
            elif bearish_alignment:
                trend = 'BEARISH'
                trend_strength = 0.5 - (combined_strength / 2)  # 0-0.5 range
            else:
                trend = 'NEUTRAL'
                trend_strength = 0.5
            
            return {
                'timeframe': timeframe,
                'trend': trend,
                'strength': trend_strength,
                'weight': self.weights.get(timeframe, 0.2),
                'emas': {
                    'ema9': float(current_ema9),
                    'ema21': float(current_ema21),
                    'ema50': float(current_ema50),
                    'aligned': bullish_alignment or bearish_alignment
                },
                'price': float(current_price),
                'momentum': float(price_change)
            }
            
        except Exception as e:
            logger.warning(f"Timeframe analysis error for {timeframe}: {e}")
            return {
                'timeframe': timeframe,
                'trend': 'NEUTRAL',
                'strength': 0.5,
                'weight': self.weights.get(timeframe, 0.2),
                'emas': {'aligned': False}
            }


class VolumeAnalyzer:
    """
    Real volume analysis to replace fake Twitter sentiment
    - VWAP (Volume-Weighted Average Price)
    - OBV (On-Balance Volume)
    - Volume Profile
    - Volume Spikes
    """
    
    def __init__(self):
        pass
    
    def analyze(self, ohlcv: pd.DataFrame) -> Dict:
        """
        Comprehensive volume analysis
        
        Returns:
            Dict with VWAP, OBV trend, volume spikes, and overall score
        """
        try:
            df = ohlcv.copy()
            
            # 1. VWAP Calculation
            vwap_result = self._calculate_vwap(df)
            
            # 2. On-Balance Volume
            obv_result = self._calculate_obv(df)
            
            # 3. Volume Spike Detection
            spike_result = self._detect_volume_spikes(df)
            
            # 4. Volume Trend
            volume_trend = self._analyze_volume_trend(df)
            
            # Combine scores
            # VWAP: 30%, OBV: 30%, Volume Spike: 20%, Volume Trend: 20%
            combined_score = (
                vwap_result['score'] * 0.30 +
                obv_result['score'] * 0.30 +
                spike_result['score'] * 0.20 +
                volume_trend['score'] * 0.20
            )
            
            # Interpretation
            if combined_score > 0.65:
                interpretation = 'STRONG_BULLISH'
                should_trade = True
            elif combined_score > 0.50:
                interpretation = 'BULLISH'
                should_trade = True
            elif combined_score < 0.35:
                interpretation = 'STRONG_BEARISH'
                should_trade = False
            elif combined_score < 0.50:
                interpretation = 'BEARISH'
                should_trade = False
            else:
                interpretation = 'NEUTRAL'
                should_trade = True
            
            result = {
                'score': combined_score,
                'interpretation': interpretation,
                'should_trade': should_trade,
                'vwap': vwap_result,
                'obv': obv_result,
                'volume_spike': spike_result,
                'volume_trend': volume_trend
            }
            
            logger.info(f"📊 Volume Analysis: {interpretation} (Score: {combined_score:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Volume analysis error: {e}", exc_info=True)
            return {
                'score': 0.5,
                'interpretation': 'NEUTRAL',
                'should_trade': True,
                'error': str(e)
            }
    
    def _calculate_vwap(self, df: pd.DataFrame) -> Dict:
        """
        VWAP: Institutional support/resistance level
        Price above VWAP = bullish, below = bearish
        """
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            current_price = df['close'].iloc[-1]
            current_vwap = vwap.iloc[-1]
            
            # Price distance from VWAP
            price_vs_vwap = (current_price - current_vwap) / current_vwap
            
            # Score: 0-1 scale
            # Above VWAP = bullish (0.5-1.0)
            # Below VWAP = bearish (0-0.5)
            if price_vs_vwap > 0:
                score = 0.5 + min(0.5, price_vs_vwap * 50)  # Cap at 1.0
            else:
                score = 0.5 + max(-0.5, price_vs_vwap * 50)  # Floor at 0.0
            
            return {
                'vwap': float(current_vwap),
                'current_price': float(current_price),
                'price_vs_vwap_pct': float(price_vs_vwap * 100),
                'score': score,
                'signal': 'ABOVE_VWAP' if price_vs_vwap > 0 else 'BELOW_VWAP'
            }
            
        except Exception as e:
            logger.warning(f"VWAP calculation error: {e}")
            return {'score': 0.5, 'signal': 'NEUTRAL'}
    
    def _calculate_obv(self, df: pd.DataFrame) -> Dict:
        """
        On-Balance Volume: Money flow indicator
        Rising OBV = accumulation (bullish)
        Falling OBV = distribution (bearish)
        """
        try:
            # OBV calculation
            obv = (df['volume'] * (~df['close'].diff().le(0) * 2 - 1)).cumsum()
            
            # OBV trend (compare current to 20 periods ago)
            current_obv = obv.iloc[-1]
            past_obv = obv.iloc[-20] if len(obv) > 20 else obv.iloc[0]
            
            obv_change = (current_obv - past_obv) / abs(past_obv) if past_obv != 0 else 0
            
            # Score based on OBV trend
            if obv_change > 0.1:
                score = 0.7  # Strong accumulation
                trend = 'RISING'
            elif obv_change > 0:
                score = 0.6  # Weak accumulation
                trend = 'RISING'
            elif obv_change < -0.1:
                score = 0.3  # Strong distribution
                trend = 'FALLING'
            elif obv_change < 0:
                score = 0.4  # Weak distribution
                trend = 'FALLING'
            else:
                score = 0.5  # Neutral
                trend = 'FLAT'
            
            return {
                'obv': float(current_obv),
                'obv_change_pct': float(obv_change * 100),
                'trend': trend,
                'score': score
            }
            
        except Exception as e:
            logger.warning(f"OBV calculation error: {e}")
            return {'score': 0.5, 'trend': 'FLAT'}
    
    def _detect_volume_spikes(self, df: pd.DataFrame) -> Dict:
        """
        Detect unusual volume (potential breakout/breakdown)
        """
        try:
            volume_sma = df['volume'].rolling(window=20).mean()
            current_volume = df['volume'].iloc[-1]
            avg_volume = volume_sma.iloc[-1]
            
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Price direction during spike
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
            
            # Score
            if volume_ratio > 2.0:  # 2x average volume
                if price_change > 0:
                    score = 0.8  # Bullish spike
                    signal = 'BULLISH_SPIKE'
                else:
                    score = 0.3  # Bearish spike
                    signal = 'BEARISH_SPIKE'
            elif volume_ratio > 1.5:  # 1.5x average
                if price_change > 0:
                    score = 0.65
                    signal = 'MODERATE_BULLISH_SPIKE'
                else:
                    score = 0.4
                    signal = 'MODERATE_BEARISH_SPIKE'
            else:
                score = 0.5
                signal = 'NORMAL_VOLUME'
            
            return {
                'current_volume': float(current_volume),
                'avg_volume': float(avg_volume),
                'volume_ratio': float(volume_ratio),
                'signal': signal,
                'score': score
            }
            
        except Exception as e:
            logger.warning(f"Volume spike detection error: {e}")
            return {'score': 0.5, 'signal': 'NORMAL_VOLUME'}
    
    def _analyze_volume_trend(self, df: pd.DataFrame) -> Dict:
        """
        Analyze if volume is increasing or decreasing over time
        """
        try:
            recent_volume = df['volume'].tail(10).mean()
            older_volume = df['volume'].iloc[-30:-10].mean() if len(df) > 30 else df['volume'].head(10).mean()
            
            volume_trend_pct = (recent_volume - older_volume) / older_volume if older_volume > 0 else 0
            
            if volume_trend_pct > 0.2:
                score = 0.7
                trend = 'INCREASING'
            elif volume_trend_pct > 0:
                score = 0.6
                trend = 'INCREASING'
            elif volume_trend_pct < -0.2:
                score = 0.4
                trend = 'DECREASING'
            elif volume_trend_pct < 0:
                score = 0.45
                trend = 'DECREASING'
            else:
                score = 0.5
                trend = 'STABLE'
            
            return {
                'recent_volume': float(recent_volume),
                'older_volume': float(older_volume),
                'trend_pct': float(volume_trend_pct * 100),
                'trend': trend,
                'score': score
            }
            
        except Exception as e:
            logger.warning(f"Volume trend analysis error: {e}")
            return {'score': 0.5, 'trend': 'STABLE'}


class LiquidityAnalyzer:
    """
    Analyze order book liquidity to prevent slippage and bad fills
    """
    
    def __init__(self, market_client):
        """
        Args:
            market_client: ccxt exchange client
        """
        self.market_client = market_client
    
    def analyze(self, symbol: str, trade_size_usd: float) -> Dict:
        """
        Check if order book has sufficient liquidity for trade
        
        Returns:
            Dict with liquidity metrics and tradeable status
        """
        try:
            # Fetch order book
            order_book = self.market_client.fetch_order_book(symbol)
            
            bids = order_book.get('bids', [])
            asks = order_book.get('asks', [])
            
            if not bids or not asks:
                logger.warning(f"Empty order book for {symbol}")
                return self._insufficient_liquidity()
            
            # Calculate mid price
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            mid_price = (best_bid + best_ask) / 2
            
            # Calculate spread
            spread = best_ask - best_bid
            spread_pct = (spread / mid_price) * 100
            
            # Calculate liquidity depth within 0.5% of mid price
            bid_depth_usd = sum(
                price * size 
                for price, size in bids[:20]  # Top 20 levels
                if price >= mid_price * 0.995
            )
            
            ask_depth_usd = sum(
                price * size 
                for price, size in asks[:20]
                if price <= mid_price * 1.005
            )
            
            # Check if trade size is reasonable vs available liquidity
            # Rule: Trade size should be < 10% of available depth
            liquidity_ratio_bid = trade_size_usd / bid_depth_usd if bid_depth_usd > 0 else float('inf')
            liquidity_ratio_ask = trade_size_usd / ask_depth_usd if ask_depth_usd > 0 else float('inf')
            liquidity_ratio = max(liquidity_ratio_bid, liquidity_ratio_ask)
            
            # Determine if tradeable
            is_tradeable = (
                liquidity_ratio < 0.1 and  # < 10% of depth
                spread_pct < 0.15  # < 0.15% spread
            )
            
            # Warning classification
            if liquidity_ratio > 0.2:
                warning = 'VERY_LOW_LIQUIDITY'
            elif liquidity_ratio > 0.1:
                warning = 'LOW_LIQUIDITY'
            elif spread_pct > 0.2:
                warning = 'WIDE_SPREAD'
            elif spread_pct > 0.1:
                warning = 'MODERATE_SPREAD'
            else:
                warning = None
            
            result = {
                'mid_price': mid_price,
                'spread': spread,
                'spread_pct': spread_pct,
                'bid_depth_usd': bid_depth_usd,
                'ask_depth_usd': ask_depth_usd,
                'liquidity_ratio': liquidity_ratio,
                'is_tradeable': is_tradeable,
                'warning': warning,
                'trade_size_usd': trade_size_usd,
                'best_bid': best_bid,
                'best_ask': best_ask
            }
            
            if not is_tradeable:
                logger.warning(f"⚠️  Low Liquidity: {symbol} - Ratio: {liquidity_ratio:.2%}, Spread: {spread_pct:.3f}%")
            else:
                logger.debug(f"✅ Sufficient Liquidity: {symbol} - Spread: {spread_pct:.3f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Liquidity analysis error: {e}", exc_info=True)
            return self._insufficient_liquidity()
    
    def _insufficient_liquidity(self) -> Dict:
        """Return result for insufficient liquidity"""
        return {
            'mid_price': 0,
            'spread': 0,
            'spread_pct': float('inf'),
            'bid_depth_usd': 0,
            'ask_depth_usd': 0,
            'liquidity_ratio': float('inf'),
            'is_tradeable': False,
            'warning': 'NO_DATA',
            'error': 'Unable to fetch order book'
        }


class CorrelationAnalyzer:
    """
    Analyze correlation between trading pairs
    Prevent trading highly correlated pairs simultaneously
    """
    
    def __init__(self, market_client):
        """
        Args:
            market_client: ccxt exchange client
        """
        self.market_client = market_client
        self.correlation_cache = {}
    
    def calculate_correlation(self, symbol1: str, symbol2: str, lookback: int = 100) -> float:
        """
        Calculate correlation between two symbols
        
        Returns:
            Correlation coefficient (-1 to +1)
            > 0.7: Highly correlated (avoid trading both)
            < -0.7: Highly inversely correlated
        """
        try:
            # Check cache first
            cache_key = f"{symbol1}_{symbol2}_{lookback}"
            if cache_key in self.correlation_cache:
                return self.correlation_cache[cache_key]
            
            # Fetch OHLCV data
            ohlcv1 = self.market_client.fetch_ohlcv(symbol1, '1h', limit=lookback)
            ohlcv2 = self.market_client.fetch_ohlcv(symbol2, '1h', limit=lookback)
            
            # Extract close prices and calculate returns
            closes1 = pd.Series([x[4] for x in ohlcv1])
            closes2 = pd.Series([x[4] for x in ohlcv2])
            
            returns1 = closes1.pct_change().dropna()
            returns2 = closes2.pct_change().dropna()
            
            # Calculate correlation
            correlation = returns1.corr(returns2)
            
            # Cache result
            self.correlation_cache[cache_key] = correlation
            
            logger.debug(f"📊 Correlation {symbol1} vs {symbol2}: {correlation:.3f}")
            
            return float(correlation) if not pd.isna(correlation) else 0.0
            
        except Exception as e:
            logger.warning(f"Correlation calculation error: {e}")
            return 0.0
    
    def should_avoid_pair(self, symbol1: str, symbol2: str, threshold: float = 0.7) -> bool:
        """
        Check if two symbols are too correlated to trade together
        
        Args:
            symbol1: First trading pair
            symbol2: Second trading pair
            threshold: Correlation threshold (default 0.7)
            
        Returns:
            True if correlation is too high (avoid trading both)
        """
        correlation = abs(self.calculate_correlation(symbol1, symbol2))
        return correlation > threshold
