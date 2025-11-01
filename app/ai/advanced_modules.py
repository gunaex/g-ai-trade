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
        
        result = {
            'regime': regime,
            'confidence': confidence,
            'allow_mean_reversion': allow_mean_reversion,
            'adx': features.iloc[-1]['adx'],
            'bb_width': features.iloc[-1]['bb_width']
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
        adx = features['adx']
        ma_ratio = features['ma_ratio']
        
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
            'bb_width': features['bb_width']
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
            # Mock implementation - replace with actual Twitter API
            # In production, use Twitter API v2 or social media aggregators
            
            # Example: CryptoPanic API (free tier available)
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token=YOUR_TOKEN&currencies={symbol}&filter=rising"
            
            # For demo, generate random sentiment
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
        """
        atr = ta.volatility.average_true_range(ohlcv['high'], ohlcv['low'], ohlcv['close'], window=period)
        return atr.iloc[-1]
    
    def calculate_volatility(self, ohlcv: pd.DataFrame) -> float:
        """
        Calculate recent volatility (standard deviation of returns)
        """
        returns = ohlcv['close'].pct_change()
        volatility = returns.std()
        return volatility
    
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
    Combines all 4 modules to make intelligent trading decisions
    """
    
    def __init__(self):
        self.regime_filter = MarketRegimeFilter()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.risk_manager = DynamicRiskManager()
        self.pattern_recognizer = MicroPatternRecognizer()
        
    def analyze(self, symbol: str, ohlcv: pd.DataFrame, order_book: Optional[dict] = None) -> Dict:
        """
        Main Analysis Pipeline
        """
        logger.info(f"🤖 Starting Advanced AI Analysis for {symbol}")
        
        try:
            # 1. Market Regime Detection
            regime = self.regime_filter.detect_regime(ohlcv)['regime']
            logger.info(f"📊 Market Regime: {regime}")
            
            # ✅ แก้ไข: อนุญาตให้เทรดใน TRENDING market
            if regime == 'SIDEWAYS':
                return {
                    'action': 'HALT',
                    'confidence': 0.0,
                    'reason': f'Market in {regime} - Not tradeable',
                    'regime': regime
                }
            
            # 2. Sentiment Analysis
            sentiment_score = self.sentiment_analyzer.get_combined_sentiment(symbol)
            twitter_sentiment = sentiment_score.get('score', 0)
            news_sentiment = sentiment_score.get('news', 0)
            combined_sentiment = (twitter_sentiment + news_sentiment) / 2
            
            logger.info(f"🐦 Twitter Sentiment for {symbol}: {twitter_sentiment:.2f}")
            logger.info(f"📰 News Sentiment for {symbol}: {news_sentiment:.2f}")
            
            sentiment_label = 'BULLISH' if combined_sentiment > 0.1 else 'BEARISH' if combined_sentiment < -0.1 else 'NEUTRAL'
            logger.info(f"💬 Combined Sentiment: {sentiment_label} ({combined_sentiment:.2f})")
            
            # ✅ แก้ไข: ลด threshold ของ sentiment
            if combined_sentiment < -0.3:  # เดิม -0.2, ปรับเป็น -0.3
                return {
                    'action': 'HOLD',
                    'confidence': 0.5,
                    'reason': f'Sentiment too negative ({combined_sentiment:.2f})',
                    'regime': regime,
                    'sentiment': combined_sentiment
                }
            
            # 3. Pattern Recognition
            reversal = self.pattern_recognizer.get_reversal_signal(ohlcv, order_book)
            patterns = reversal.get('patterns_detected', [])
            
            if not patterns:
                logger.info("❌ No patterns detected")
                # ✅ แก้ไข: ถ้าไม่มี pattern แต่ trend + sentiment ดี ก็ให้เทรดได้
                if regime == 'TRENDING_UP' and combined_sentiment >= 0:
                    logger.info("✅ No pattern but TRENDING_UP + positive sentiment -> BUY")
                    # Continue to risk management
                    patterns = [{'type': 'trend_following', 'strength': 0.6}]
                elif regime == 'TRENDING_DOWN' and combined_sentiment <= 0:
                    logger.info("✅ No pattern but TRENDING_DOWN + negative sentiment -> SELL")
                    patterns = [{'type': 'trend_following', 'strength': 0.6}]
                else:
                    return {
                        'action': 'HOLD',
                        'confidence': 0.4,
                        'reason': 'No clear patterns detected',
                        'regime': regime,
                        'sentiment': combined_sentiment
                    }
            
            logger.info(f"🔍 Patterns Detected: {len(patterns)} patterns")
            
            # 4. Dynamic Risk Management
            current_price = ohlcv['close'].iloc[-1]
            risk_levels = self.risk_manager.get_dynamic_levels(ohlcv, current_price)
            
            stop_loss_pct = risk_levels['stop_loss_pct']
            take_profit_pct = risk_levels['take_profit_pct']
            risk_reward = risk_levels['risk_reward_ratio']
            
            logger.info(f"🎯 Dynamic Levels: SL={stop_loss_pct:.2f}%, TP={take_profit_pct:.2f}%, R:R={risk_reward:.2f}")
            
            # ✅ Final Decision Logic
            # ถ้า TRENDING_UP + sentiment ไม่ติดลบมาก + มี pattern
            if regime == 'TRENDING_UP':
                action = 'BUY'
                confidence = 0.7 + (combined_sentiment * 0.2)  # 0.7-0.9
                reason = f"Trend: UP | Sentiment: {sentiment_label} | Patterns: {len(patterns)}"
            
            elif regime == 'TRENDING_DOWN':
                action = 'SELL'
                confidence = 0.7 + (abs(combined_sentiment) * 0.2)
                reason = f"Trend: DOWN | Sentiment: {sentiment_label} | Patterns: {len(patterns)}"
            
            else:
                action = 'HOLD'
                confidence = 0.5
                reason = f"Market regime {regime} - waiting for clear signal"
            
            logger.info(f"✅ Advanced AI Decision: {action} (Confidence: {confidence*100:.2f}%)")
            logger.info(f"   Reason: {reason}")
            
            return {
                'action': action,
                'confidence': confidence,
                'reason': reason,
                'regime': regime,
                'sentiment': combined_sentiment,
                'patterns': patterns,
                'stop_loss_percent': stop_loss_pct,
                'take_profit_percent': take_profit_pct,
                'risk_reward_ratio': risk_reward
            }
            
        except Exception as e:
            logger.error(f"Advanced AI Analysis Error: {e}")
            return {
                'action': 'HALT',
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'regime': 'UNKNOWN'
            }