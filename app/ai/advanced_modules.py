import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
# Import TA-Lib
import ta  # Using ta package instead of talib for now
import requests
from textblob import TextBlob

# Import new advanced modules
from app.ai.risk_management import PositionSizer, AdaptiveStopLoss, PerformanceTracker
from app.ai.market_analysis import MultiTimeframeAnalyzer, VolumeAnalyzer, LiquidityAnalyzer, CorrelationAnalyzer

logger = logging.getLogger(__name__)

# ============================================================================
# MODULE 1: Market Regime Filter
# ============================================================================

class MarketRegimeFilter:
    """
    Detect market condition: Trending Up, Trending Down, or Sideways
    Uses Technical Indicators + ML Classification
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.regime = "UNKNOWN"  # TRENDING_UP, TRENDING_DOWN, SIDEWAYS
        
    def calculate_features(self, ohlcv: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators as features
        Input: OHLCV DataFrame
        Output: Feature DataFrame
        """
        df = ohlcv.copy()
        
        # ADX (Average Directional Index) - Trend Strength
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
        
        # Bollinger Bands Width - Volatility
        indicator_bb = ta.volatility.BollingerBands(df['close'], window=20)
        upper = indicator_bb.bollinger_hband()
        middle = indicator_bb.bollinger_mavg()
        lower = indicator_bb.bollinger_lband()
        df['bb_width'] = (upper - lower) / middle
        
        # Moving Averages
        df['sma_20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50)
        df['ma_ratio'] = df['sma_20'] / df['sma_50']  # Trend direction
        
        # RSI (Relative Strength Index)
        df['rsi'] = ta.momentum.rsi(df['close'], window=14)
        
        # Volume Trend
        df['volume_sma'] = ta.trend.sma_indicator(df['volume'], window=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price Rate of Change
        df['roc'] = ta.momentum.roc(df['close'], window=10)
        
        return df[['adx', 'bb_width', 'ma_ratio', 'rsi', 'volume_ratio', 'roc']].dropna()
    
    def train_model(self, historical_data: pd.DataFrame, labels: List[str]):
        """
        Train Random Forest classifier to detect market regime
        Labels: ['TRENDING_UP', 'TRENDING_DOWN', 'SIDEWAYS']
        """
        features = self.calculate_features(historical_data)
        
        # Prepare training data
        X = self.scaler.fit_transform(features)
        y = labels[-len(X):]  # Match length
        
        # Train Random Forest
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        logger.info("✅ Market Regime Filter model trained")
    
    def detect_regime(self, ohlcv: pd.DataFrame) -> Dict[str, any]:
        """
        Detect current market regime
        Returns: {regime: str, confidence: float, allow_mean_reversion: bool}
        """
        features = self.calculate_features(ohlcv)
        
        if self.model is None:
            # Use rule-based fallback
            return self._rule_based_detection(features.iloc[-1])
        
        # ML-based detection
        X = self.scaler.transform(features.iloc[-1:])
        regime = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X).max()
        
        # Mean Reversion works best in SIDEWAYS market
        allow_mean_reversion = (regime == 'SIDEWAYS')
        
        # Handle NaN values in features
        adx_val = features.iloc[-1]['adx']
        bb_width_val = features.iloc[-1]['bb_width']
        adx_val = float(adx_val) if not pd.isna(adx_val) else 25.0
        bb_width_val = float(bb_width_val) if not pd.isna(bb_width_val) else 0.02
        
        result = {
            'regime': regime,
            'confidence': confidence,
            'allow_mean_reversion': allow_mean_reversion,
            'adx': adx_val,
            'bb_width': bb_width_val
        }
        
        self.regime = regime
        logger.info(f"📊 Market Regime: {regime} (Confidence: {confidence:.2%})")
        
        return result
    
    def _rule_based_detection(self, features: pd.Series) -> Dict[str, any]:
        """
        Fallback rule-based regime detection using ADX
        ADX < 20: Weak trend (SIDEWAYS)
        ADX > 40: Strong trend (TRENDING)
        """
        # Handle NaN values
        adx = float(features['adx']) if not pd.isna(features['adx']) else 25.0  # Default to medium
        ma_ratio = float(features['ma_ratio']) if not pd.isna(features['ma_ratio']) else 1.0
        bb_width = float(features['bb_width']) if not pd.isna(features['bb_width']) else 0.02
        
        if adx < 20:
            regime = 'SIDEWAYS'
        elif adx > 40:
            regime = 'TRENDING_UP' if ma_ratio > 1 else 'TRENDING_DOWN'
        else:
            # Medium trend
            regime = 'SIDEWAYS' if abs(ma_ratio - 1) < 0.02 else ('TRENDING_UP' if ma_ratio > 1 else 'TRENDING_DOWN')
        
        return {
            'regime': regime,
            'confidence': 0.7,
            'allow_mean_reversion': (regime == 'SIDEWAYS'),
            'adx': adx,
            'bb_width': bb_width
        }


# ============================================================================
# MODULE 2: Sentiment Analysis
# ============================================================================

class SentimentAnalyzer:
    """
    Analyze market sentiment from news and social media
    Uses NLP (TextBlob / VADER)
    """
    
    def __init__(self):
        self.sentiment_score = 0.0  # -1 (bearish) to +1 (bullish)
        
    def fetch_twitter_sentiment(self, symbol: str) -> float:
        """
        Fetch and analyze Twitter sentiment for crypto symbol
        Returns: sentiment score -1 to +1
        """
        try:
            # Mock implementation - using fast random generation
            # In production, replace with actual Twitter API or sentiment service
            import random
            sentiment = random.uniform(-0.3, 0.3)
            
            logger.info(f"🐦 Twitter Sentiment for {symbol}: {sentiment:.2f}")
            return sentiment
            
        except Exception as e:
            logger.error(f"Twitter sentiment error: {e}")
            return 0.0
    
    def analyze_news_sentiment(self, symbol: str) -> float:
        """
        Analyze sentiment from crypto news headlines
        Uses TextBlob for sentiment analysis
        """
        try:
            # Mock news headlines (replace with actual news API)
            # Example: CoinGecko, CryptoPanic, NewsAPI
            
            headlines = [
                f"{symbol} surges to new highs",
                f"Analysts predict {symbol} rally",
                f"{symbol} faces resistance"
            ]
            
            sentiments = []
            for headline in headlines:
                blob = TextBlob(headline)
                sentiments.append(blob.sentiment.polarity)
            
            avg_sentiment = np.mean(sentiments) if sentiments else 0.0
            
            logger.info(f"📰 News Sentiment for {symbol}: {avg_sentiment:.2f}")
            return avg_sentiment
            
        except Exception as e:
            logger.error(f"News sentiment error: {e}")
            return 0.0
    
    def get_combined_sentiment(self, symbol: str) -> Dict[str, any]:
        """
        Get combined sentiment score from multiple sources
        Returns: {score: float, interpretation: str, should_trade: bool}
        """
        twitter_sentiment = self.fetch_twitter_sentiment(symbol)
        news_sentiment = self.analyze_news_sentiment(symbol)
        
        # Weighted average (adjust weights as needed)
        combined = (twitter_sentiment * 0.6 + news_sentiment * 0.4)
        
        # Clamp to -1 to +1
        combined = max(-1.0, min(1.0, combined))
        
        # Interpretation
        if combined > 0.3:
            interpretation = "VERY_BULLISH"
            should_trade = True
        elif combined > 0.1:
            interpretation = "BULLISH"
            should_trade = True
        elif combined < -0.3:
            interpretation = "VERY_BEARISH"
            should_trade = False  # Avoid buying
        elif combined < -0.1:
            interpretation = "BEARISH"
            should_trade = False
        else:
            interpretation = "NEUTRAL"
            should_trade = True
        
        result = {
            'score': combined,
            'interpretation': interpretation,
            'should_trade': should_trade,
            'twitter': twitter_sentiment,
            'news': news_sentiment
        }
        
        self.sentiment_score = combined
        logger.info(f"💬 Combined Sentiment: {interpretation} ({combined:.2f})")
        
        return result


# ============================================================================
# MODULE 3: Dynamic Risk Management
# ============================================================================

class DynamicRiskManager:
    """
    Calculate dynamic Stop Loss and Take Profit based on volatility
    Uses ATR (Average True Range)
    """
    
    def __init__(self):
        self.stop_loss_pct = 0.02  # Default 2%
        self.take_profit_pct = 0.04  # Default 4%
        
    def calculate_atr(self, ohlcv: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR)
        Returns 0.0 if calculation fails or data insufficient
        """
        try:
            atr = ta.volatility.average_true_range(ohlcv['high'], ohlcv['low'], ohlcv['close'], window=period)
            atr_value = atr.iloc[-1]
            if pd.isna(atr_value) or np.isnan(atr_value):
                # Fallback: use price-based estimate
                recent_high = ohlcv['high'].tail(period).max()
                recent_low = ohlcv['low'].tail(period).min()
                return (recent_high - recent_low) / period if recent_high > recent_low else ohlcv['close'].iloc[-1] * 0.01
            return float(atr_value)
        except Exception as e:
            logger.warning(f"ATR calculation failed: {e}, using fallback")
            # Fallback: 1% of current price
            return ohlcv['close'].iloc[-1] * 0.01
    
    def calculate_volatility(self, ohlcv: pd.DataFrame) -> float:
        """
        Calculate recent volatility (standard deviation of returns)
        Returns 0.02 (2%) if calculation fails
        """
        try:
            returns = ohlcv['close'].pct_change().dropna()
            if len(returns) < 2:
                return 0.02  # Default 2% volatility
            volatility = returns.std()
            if pd.isna(volatility) or np.isnan(volatility):
                return 0.02
            return float(volatility)
        except Exception as e:
            logger.warning(f"Volatility calculation failed: {e}, using fallback")
            return 0.02  # Default 2% volatility
    
    def get_dynamic_levels(self, ohlcv: pd.DataFrame, entry_price: float) -> Dict[str, float]:
        """
        Calculate dynamic Stop Loss and Take Profit levels
        
        Returns: {
            stop_loss_price: float,
            take_profit_price: float,
            stop_loss_pct: float,
            take_profit_pct: float,
            risk_reward_ratio: float
        }
        """
        current_price = ohlcv['close'].iloc[-1]
        atr = self.calculate_atr(ohlcv)
        volatility = self.calculate_volatility(ohlcv)
        
        # Dynamic adjustment based on volatility
        # High volatility → wider stops
        # Low volatility → tighter stops
        
        volatility_multiplier = max(1.0, min(3.0, volatility / 0.02))  # Normalize to 0.02 baseline
        
        # ATR-based calculation
        atr_multiplier = 1.5  # Adjust this for sensitivity
        
        # Stop Loss: use ATR
        sl_distance = atr * atr_multiplier * volatility_multiplier
        stop_loss_price = entry_price - sl_distance
        stop_loss_pct = (sl_distance / entry_price) * 100
        
        # Take Profit: 2x risk (Risk:Reward = 1:2)
        tp_distance = sl_distance * 2
        take_profit_price = entry_price + tp_distance
        take_profit_pct = (tp_distance / entry_price) * 100
        
        # Risk-Reward Ratio
        risk_reward_ratio = tp_distance / sl_distance
        
        result = {
            'stop_loss_price': stop_loss_price,
            'take_profit_price': take_profit_price,
            'stop_loss_pct': stop_loss_pct,
            'take_profit_pct': take_profit_pct,
            'risk_reward_ratio': risk_reward_ratio,
            'atr': atr,
            'volatility': volatility
        }
        
        logger.info(f"🎯 Dynamic Levels: SL={stop_loss_pct:.2f}%, TP={take_profit_pct:.2f}%, R:R={risk_reward_ratio:.2f}")
        
        return result


# ============================================================================
# MODULE 4: Micro-Pattern Recognition
# ============================================================================

class MicroPatternRecognizer:
    """
    Detect reversal patterns using candlestick analysis and order book
    Uses ML (SVM/Random Forest) for pattern recognition
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def detect_candlestick_patterns(self, ohlcv: pd.DataFrame) -> Dict[str, int]:
        """
        Detect bullish/bearish candlestick patterns using TA-Lib
        Returns: {pattern_name: signal} where signal: +100 (bullish), -100 (bearish), 0 (none)
        """
        patterns = {}
        
        # Note: ta library doesn't have direct candlestick pattern functions
        # Using simplified pattern detection
        hammer = ((ohlcv['close'] - ohlcv['low']) > 3 * (ohlcv['open'] - ohlcv['close'])) & \
                ((ohlcv['high'] - ohlcv['close']) < (ohlcv['open'] - ohlcv['low']))
        patterns['hammer'] = 100 if hammer.iloc[-1] else 0
        
        engulfing = (ohlcv['open'].shift(1) > ohlcv['close'].shift(1)) & \
                   (ohlcv['close'] > ohlcv['open']) & \
                   (ohlcv['open'] < ohlcv['close'].shift(1)) & \
                   (ohlcv['close'] > ohlcv['open'].shift(1))
        patterns['engulfing_bull'] = 100 if engulfing.iloc[-1] else 0
        
        # Simplified morning star and evening star patterns
        morning_star = (ohlcv['close'].shift(2) > ohlcv['open'].shift(2)) & \
                      (ohlcv['open'].shift(1) < ohlcv['close'].shift(2)) & \
                      (ohlcv['close'] > ohlcv['open'])
        patterns['morning_star'] = 100 if morning_star.iloc[-1] else 0
        
        # Bearish patterns
        shooting_star = ((ohlcv['high'] - ohlcv['close']) > 3 * (ohlcv['close'] - ohlcv['open'])) & \
                       ((ohlcv['close'] - ohlcv['low']) < (ohlcv['high'] - ohlcv['close']))
        patterns['shooting_star'] = -100 if shooting_star.iloc[-1] else 0
        
        engulfing_bear = (ohlcv['close'].shift(1) > ohlcv['open'].shift(1)) & \
                        (ohlcv['open'] > ohlcv['close']) & \
                        (ohlcv['close'] < ohlcv['open'].shift(1)) & \
                        (ohlcv['open'] > ohlcv['close'].shift(1))
        patterns['engulfing_bear'] = -100 if engulfing_bear.iloc[-1] else 0
        
        evening_star = (ohlcv['close'].shift(2) < ohlcv['open'].shift(2)) & \
                      (ohlcv['open'].shift(1) > ohlcv['close'].shift(2)) & \
                      (ohlcv['close'] < ohlcv['open'])
        patterns['evening_star'] = -100 if evening_star.iloc[-1] else 0
        
        return patterns
    
    def analyze_order_book_imbalance(self, order_book: Dict) -> float:
        """
        Analyze bid-ask imbalance from order book
        Returns: imbalance score -1 (sell pressure) to +1 (buy pressure)
        """
        try:
            # Calculate total bid/ask volume
            bid_volume = sum([float(bid[1]) for bid in order_book.get('bids', [])[:10]])
            ask_volume = sum([float(ask[1]) for ask in order_book.get('asks', [])[:10]])
            
            if bid_volume + ask_volume == 0:
                return 0.0
            
            # Imbalance: positive = more buyers, negative = more sellers
            imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
            
            return imbalance
            
        except Exception as e:
            logger.error(f"Order book analysis error: {e}")
            return 0.0
    
    def get_reversal_signal(self, ohlcv: pd.DataFrame, order_book: Dict = None) -> Dict[str, any]:
        """
        Get micro-level reversal confirmation signal
        
        Returns: {
            is_bullish_reversal: bool,
            is_bearish_reversal: bool,
            confidence: float,
            patterns_detected: List[str]
        }
        """
        # Detect candlestick patterns
        patterns = self.detect_candlestick_patterns(ohlcv)
        
        # Count bullish vs bearish signals
        bullish_signals = sum([1 for p, v in patterns.items() if v > 0])
        bearish_signals = sum([1 for p, v in patterns.items() if v < 0])
        
        # Order book imbalance
        imbalance = 0.0
        if order_book:
            imbalance = self.analyze_order_book_imbalance(order_book)
        
        # Combine signals
        is_bullish_reversal = (bullish_signals >= 2) or (bullish_signals >= 1 and imbalance > 0.3)
        is_bearish_reversal = (bearish_signals >= 2) or (bearish_signals >= 1 and imbalance < -0.3)
        
        # Confidence calculation
        total_signals = bullish_signals + bearish_signals
        confidence = min(1.0, (total_signals / 3) + abs(imbalance))
        
        patterns_detected = [name for name, value in patterns.items() if value != 0]
        
        result = {
            'is_bullish_reversal': is_bullish_reversal,
            'is_bearish_reversal': is_bearish_reversal,
            'confidence': confidence,
            'patterns_detected': patterns_detected,
            'order_book_imbalance': imbalance
        }
        
        if is_bullish_reversal:
            logger.info(f"🟢 Bullish Reversal Detected (Confidence: {confidence:.2%})")
        elif is_bearish_reversal:
            logger.info(f"🔴 Bearish Reversal Detected (Confidence: {confidence:.2%})")
        
        return result


# ============================================================================
# MAIN: Advanced AI Trading Engine
# ============================================================================

class AdvancedAITradingEngine:
    """
    Combines all modules to make intelligent trading decisions
    
    Core Modules:
    - Market Regime Filter
    - Volume Analyzer (replaces fake sentiment)
    - Dynamic Risk Manager
    - Pattern Recognizer
    
    Advanced Modules:
    - Multi-Timeframe Analyzer
    - Position Sizer (Kelly Criterion)
    - Adaptive Stop Loss
    - Liquidity Analyzer
    - Performance Tracker
    """
    
    def __init__(self, market_client=None):
        # Core modules
        self.regime_filter = MarketRegimeFilter()
        self.volume_analyzer = VolumeAnalyzer()  # Replaces SentimentAnalyzer
        self.risk_manager = DynamicRiskManager()
        self.pattern_recognizer = MicroPatternRecognizer()
        
        # Advanced modules
        self.market_client = market_client
        if market_client:
            self.mtf_analyzer = MultiTimeframeAnalyzer(market_client)
            self.liquidity_analyzer = LiquidityAnalyzer(market_client)
            self.correlation_analyzer = CorrelationAnalyzer(market_client)
        else:
            self.mtf_analyzer = None
            self.liquidity_analyzer = None
            self.correlation_analyzer = None
        
        self.position_sizer = PositionSizer(max_risk_per_trade=0.02)
        self.performance_tracker = PerformanceTracker()
        
        # Keep old sentiment analyzer for backward compatibility but mark as deprecated
        self.sentiment_analyzer = SentimentAnalyzer()
        
    def analyze(self, symbol: str, ohlcv: pd.DataFrame, order_book: Optional[dict] = None,
                account_balance: float = 10000.0, confidence_override: Optional[float] = None) -> Dict:
        """
        Main Analysis Pipeline with Advanced Features
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            ohlcv: OHLCV DataFrame
            order_book: Optional order book data
            account_balance: Account balance for position sizing
            confidence_override: Optional confidence override
        
        Returns:
            Comprehensive analysis with action, risk levels, position size, etc.
        """
        logger.info(f"🤖 Starting Advanced AI Analysis for {symbol}")
        
        try:
            # 1. Market Regime Detection
            regime_result = self.regime_filter.detect_regime(ohlcv)
            regime = regime_result.get('regime', 'UNKNOWN')
            logger.info(f"📊 Market Regime: {regime}")

            # 2. Multi-Timeframe Analysis (if available)
            mtf_result = None
            if self.mtf_analyzer:
                try:
                    mtf_result = self.mtf_analyzer.analyze(symbol)
                    logger.info(f"📈 Multi-TF: {mtf_result.get('alignment', 'N/A')} (Conf: {mtf_result.get('confidence', 0)*100:.1f}%)")
                except Exception as e:
                    logger.warning(f"Multi-timeframe analysis failed: {e}")

            # 3. Volume Analysis (replaces fake sentiment)
            volume_result = self.volume_analyzer.analyze(ohlcv)
            volume_score = volume_result.get('score', 0.5)
            logger.info(f"� Volume Analysis: {volume_result.get('interpretation', 'NEUTRAL')} (Score: {volume_score:.2f})")

            # 4. Pattern Recognition
            reversal_result = self.pattern_recognizer.get_reversal_signal(ohlcv, order_book)
            patterns = reversal_result.get('patterns_detected', []) or []

            # Early exit checks
            current_price = float(ohlcv['close'].iloc[-1])
            
            # Compute fallback risk levels
            try:
                risk_levels_early = self.risk_manager.get_dynamic_levels(ohlcv, current_price)
                if risk_levels_early.get('atr') is None or pd.isna(risk_levels_early.get('atr')):
                    raise ValueError("ATR is None")
            except Exception as e:
                logger.warning(f"Risk levels calculation failed: {e}, using fallback defaults")
                sl_pct = 2.0
                tp_pct = 4.0
                risk_levels_early = {
                    'stop_loss_price': current_price * (1 - sl_pct / 100),
                    'take_profit_price': current_price * (1 + tp_pct / 100),
                    'stop_loss_pct': sl_pct,
                    'take_profit_pct': tp_pct,
                    'risk_reward_ratio': 2.0,
                    'atr': current_price * 0.01,
                    'volatility': 0.02
                }

            # Normalize helper
            def _f(v):
                try:
                    if v is None:
                        return None
                    fval = float(v)
                    if pd.isna(fval) or np.isnan(fval):
                        return None
                    return fval
                except (ValueError, TypeError, OverflowError):
                    return None

            # Build normalized regime object
            adx_val = _f(regime_result.get('adx'))
            bb_width_val = _f(regime_result.get('bb_width'))
            
            regime_obj = {
                'regime': regime_result.get('regime', 'UNKNOWN'),
                'confidence': float(regime_result.get('confidence', 0.0) or 0.0),
                'allow_mean_reversion': bool(regime_result.get('allow_mean_reversion', False)),
                'adx': adx_val if adx_val is not None else 0.0,
                'bb_width': bb_width_val if bb_width_val is not None else 0.0
            }

            # Build volume object (replaces sentiment)
            volume_obj = {
                'score': _f(volume_result.get('score', 0.5)),
                'interpretation': volume_result.get('interpretation', 'NEUTRAL'),
                'should_trade': bool(volume_result.get('should_trade', True)),
                'vwap': volume_result.get('vwap', {}),
                'obv': volume_result.get('obv', {}),
                'volume_spike': volume_result.get('volume_spike', {})
            }

            risk_obj = {
                'stop_loss_price': _f(risk_levels_early.get('stop_loss_price')),
                'take_profit_price': _f(risk_levels_early.get('take_profit_price')),
                'stop_loss_pct': _f(risk_levels_early.get('stop_loss_pct')),
                'take_profit_pct': _f(risk_levels_early.get('take_profit_pct')),
                'atr': _f(risk_levels_early.get('atr')),
                'volatility': _f(risk_levels_early.get('volatility'))
            }

            reversal_empty = {
                'is_bullish_reversal': False,
                'is_bearish_reversal': False,
                'confidence': 0.0,
                'patterns_detected': [],
                'order_book_imbalance': 0.0
            }

            # Early exit: SIDEWAYS market
            if regime == 'SIDEWAYS' and not patterns:
                return {
                    'action': 'HALT',
                    'confidence': 0.0,
                    'reason': f'Market in {regime} - Not tradeable',
                    'current_price': current_price,
                    'stop_loss': risk_obj['stop_loss_price'],
                    'take_profit': risk_obj['take_profit_price'],
                    'risk_reward_ratio': _f(risk_levels_early.get('risk_reward_ratio')),
                    'modules': {
                        'regime': regime_obj,
                        'volume': volume_obj,  # Changed from sentiment
                        'risk_levels': risk_obj,
                        'reversal': reversal_empty,
                        'mtf': mtf_result
                    }
                }

            # Early exit: Very negative volume sentiment
            if volume_score < 0.35:
                return {
                    'action': 'HOLD',
                    'confidence': 0.5,
                    'reason': f'Volume analysis too negative ({volume_score:.2f})',
                    'current_price': current_price,
                    'stop_loss': risk_obj['stop_loss_price'],
                    'take_profit': risk_obj['take_profit_price'],
                    'risk_reward_ratio': _f(risk_levels_early.get('risk_reward_ratio')),
                    'modules': {
                        'regime': regime_obj,
                        'volume': volume_obj,
                        'risk_levels': risk_obj,
                        'reversal': reversal_empty,
                        'mtf': mtf_result
                    }
                }

            # Multi-timeframe check
            mtf_confidence_boost = 0.0
            if mtf_result and mtf_result.get('alignment') == 'STRONG_BULLISH':
                mtf_confidence_boost = 0.15
            elif mtf_result and mtf_result.get('alignment') == 'STRONG_BEARISH':
                mtf_confidence_boost = 0.15

            # Pattern analysis
            if not patterns:
                logger.info("❌ No patterns detected")
                # Allow trend-following fallback
                if regime == 'TRENDING_UP' and volume_score >= 0.5:
                    logger.info("✅ No pattern but TRENDING_UP + positive volume -> BUY (trend-following)")
                    patterns = [{'type': 'trend_following', 'strength': 0.6}]
                elif regime == 'TRENDING_DOWN' and volume_score <= 0.5:
                    logger.info("✅ No pattern but TRENDING_DOWN + negative volume -> SELL (trend-following)")
                    patterns = [{'type': 'trend_following', 'strength': 0.6}]
                else:
                    return {
                        'action': 'HOLD',
                        'confidence': 0.4,
                        'reason': 'No clear patterns detected',
                        'current_price': current_price,
                        'stop_loss': risk_obj['stop_loss_price'],
                        'take_profit': risk_obj['take_profit_price'],
                        'risk_reward_ratio': _f(risk_levels_early.get('risk_reward_ratio')),
                        'modules': {
                            'regime': regime_obj,
                            'volume': volume_obj,
                            'risk_levels': risk_obj,
                            'reversal': {
                                'is_bullish_reversal': reversal_result.get('is_bullish_reversal', False),
                                'is_bearish_reversal': reversal_result.get('is_bearish_reversal', False),
                                'confidence': reversal_result.get('confidence', 0.0),
                                'patterns_detected': reversal_result.get('patterns_detected', []),
                                'order_book_imbalance': reversal_result.get('order_book_imbalance', 0.0)
                            },
                            'mtf': mtf_result
                        }
                    }

            logger.info(f"🔍 Patterns Detected: {len(patterns)} patterns")

            # 5. Dynamic Risk Management
            risk_levels = self.risk_manager.get_dynamic_levels(ohlcv, current_price)

            stop_loss_price = risk_levels.get('stop_loss_price')
            take_profit_price = risk_levels.get('take_profit_price')
            stop_loss_pct = risk_levels.get('stop_loss_pct')
            take_profit_pct = risk_levels.get('take_profit_pct')
            risk_reward = risk_levels.get('risk_reward_ratio')

            logger.info(f"🎯 Dynamic Levels: SL={stop_loss_pct:.2f}%, TP={take_profit_pct:.2f}%, R:R={risk_reward:.2f}")

            risk_obj_final = {
                'stop_loss_price': _f(stop_loss_price),
                'take_profit_price': _f(take_profit_price),
                'stop_loss_pct': _f(stop_loss_pct),
                'take_profit_pct': _f(take_profit_pct),
                'atr': _f(risk_levels.get('atr')),
                'volatility': _f(risk_levels.get('volatility'))
            }

            # 6. Final Decision Logic with Multi-Timeframe Integration
            base_confidence = 0.7
            
            # Adjust confidence based on volume analysis
            volume_adjustment = (volume_score - 0.5) * 0.4  # -0.2 to +0.2
            
            if regime == 'TRENDING_UP':
                action = 'BUY'
                confidence = base_confidence + volume_adjustment + mtf_confidence_boost
                reason = f"Trend: UP | Volume: {volume_result.get('interpretation', 'N/A')} | Patterns: {len(patterns)}"
                
                # Add multi-timeframe info if available
                if mtf_result:
                    reason += f" | MTF: {mtf_result.get('alignment', 'N/A')}"
                    
            elif regime == 'TRENDING_DOWN':
                action = 'SELL'
                confidence = base_confidence + abs(volume_adjustment) + mtf_confidence_boost
                reason = f"Trend: DOWN | Volume: {volume_result.get('interpretation', 'N/A')} | Patterns: {len(patterns)}"
                
                if mtf_result:
                    reason += f" | MTF: {mtf_result.get('alignment', 'N/A')}"
            else:
                action = 'HOLD'
                confidence = 0.5
                reason = f"Market regime {regime} - waiting for clear signal"

            # Cap confidence at 0.95
            confidence = max(0.0, min(0.95, confidence))
            
            # Override confidence if provided
            if confidence_override is not None:
                confidence = confidence_override

            # 7. Position Sizing (new feature)
            performance_stats = self.performance_tracker.get_statistics(lookback_days=30)
            position_size_info = self.position_sizer.calculate_position_size(
                account_balance=account_balance,
                win_rate=performance_stats.get('win_rate', 0.5),
                avg_win_pct=performance_stats.get('avg_win_pct', 0.03),
                avg_loss_pct=performance_stats.get('avg_loss_pct', 0.02),
                current_volatility=risk_levels.get('volatility', 0.02),
                confidence=confidence
            )

            logger.info(f"✅ Advanced AI Decision: {action} (Confidence: {confidence*100:.2f}%)")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   Position Size: ${position_size_info['position_size_usd']:.2f} ({position_size_info['position_pct']:.2f}%)")

            # Build comprehensive response
            response = {
                'action': action,
                'confidence': confidence,
                'reason': reason,
                'current_price': current_price,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'risk_reward_ratio': risk_reward,
                'position_size_usd': position_size_info['position_size_usd'],
                'position_pct': position_size_info['position_pct'],
                'modules': {
                    'regime': regime_obj,
                    'volume': volume_obj,  # Replaces sentiment
                    'risk_levels': risk_obj_final,
                    'reversal': {
                        'is_bullish_reversal': reversal_result.get('is_bullish_reversal', False),
                        'is_bearish_reversal': reversal_result.get('is_bearish_reversal', False),
                        'confidence': reversal_result.get('confidence', 0.0),
                        'patterns_detected': reversal_result.get('patterns_detected', []),
                        'order_book_imbalance': reversal_result.get('order_book_imbalance', 0.0)
                    },
                    'mtf': mtf_result,
                    'position_sizing': position_size_info,
                    'performance': performance_stats
                }
            }

            return response
            
        except Exception as e:
            logger.error(f"Advanced AI Analysis Error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Always return full structure even on error
            current_price = float(ohlcv['close'].iloc[-1]) if len(ohlcv) > 0 else 0.0
            
            fallback_risk = {
                'stop_loss_price': current_price * 0.98 if current_price > 0 else None,
                'take_profit_price': current_price * 1.04 if current_price > 0 else None,
                'stop_loss_pct': 2.0,
                'take_profit_pct': 4.0,
                'risk_reward_ratio': 2.0,
                'atr': current_price * 0.01 if current_price > 0 else 0.0,
                'volatility': 0.02
            }
            
            return {
                'action': 'HALT',
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'current_price': current_price,
                'stop_loss': fallback_risk['stop_loss_price'],
                'take_profit': fallback_risk['take_profit_price'],
                'risk_reward_ratio': fallback_risk['risk_reward_ratio'],
                'position_size_usd': account_balance * 0.01,
                'position_pct': 1.0,
                'modules': {
                    'regime': {
                        'regime': 'UNKNOWN',
                        'confidence': 0.0,
                        'allow_mean_reversion': False,
                        'adx': 0.0,
                        'bb_width': 0.0
                    },
                    'volume': {
                        'score': 0.5,
                        'interpretation': 'NEUTRAL',
                        'should_trade': False
                    },
                    'risk_levels': fallback_risk,
                    'reversal': {
                        'is_bullish_reversal': False,
                        'is_bearish_reversal': False,
                        'confidence': 0.0,
                        'patterns_detected': [],
                        'order_book_imbalance': 0.0
                    }
                }
            }