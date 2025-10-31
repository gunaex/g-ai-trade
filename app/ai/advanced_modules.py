import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import talib
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
        df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
        
        # Bollinger Bands Width - Volatility
        upper, middle, lower = talib.BBANDS(df['close'], timeperiod=20)
        df['bb_width'] = (upper - lower) / middle
        
        # Moving Averages
        df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
        df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
        df['ma_ratio'] = df['sma_20'] / df['sma_50']  # Trend direction
        
        # RSI (Relative Strength Index)
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        
        # Volume Trend
        df['volume_sma'] = talib.SMA(df['volume'], timeperiod=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price Rate of Change
        df['roc'] = talib.ROC(df['close'], timeperiod=10)
        
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
        atr = talib.ATR(ohlcv['high'], ohlcv['low'], ohlcv['close'], timeperiod=period)
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
        
        # Bullish patterns
        patterns['hammer'] = talib.CDLHAMMER(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        patterns['engulfing_bull'] = talib.CDLENGULFING(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        patterns['morning_star'] = talib.CDLMORNINGSTAR(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        
        # Bearish patterns
        patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        patterns['engulfing_bear'] = talib.CDLENGULFING(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        patterns['evening_star'] = talib.CDLEVENINGSTAR(ohlcv['open'], ohlcv['high'], ohlcv['low'], ohlcv['close']).iloc[-1]
        
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
        
    def analyze(self, symbol: str, ohlcv: pd.DataFrame, order_book: Dict = None) -> Dict[str, any]:
        """
        Full AI analysis combining all 4 modules
        
        Returns comprehensive trading decision with reasoning
        """
        logger.info(f"🤖 Starting Advanced AI Analysis for {symbol}")
        
        # Module 1: Market Regime
        regime = self.regime_filter.detect_regime(ohlcv)
        
        # Module 2: Sentiment
        sentiment = self.sentiment_analyzer.get_combined_sentiment(symbol)
        
        # Module 3: Dynamic Risk Levels
        current_price = ohlcv['close'].iloc[-1]
        risk_levels = self.risk_manager.get_dynamic_levels(ohlcv, current_price)
        
        # Module 4: Micro-Pattern Recognition
        reversal = self.pattern_recognizer.get_reversal_signal(ohlcv, order_book)
        
        # === DECISION LOGIC ===
        
        # Check if Mean Reversion is allowed (only in SIDEWAYS market)
        if not regime['allow_mean_reversion']:
            action = 'HALT'
            reason = f"Market in {regime['regime']} - Mean Reversion disabled"
            confidence = 0.0
        
        # Check sentiment filter
        elif not sentiment['should_trade']:
            action = 'HALT'
            reason = f"Negative sentiment: {sentiment['interpretation']}"
            confidence = 0.0
        
        # BUY signal: Bullish reversal + Positive sentiment
        elif reversal['is_bullish_reversal'] and sentiment['score'] > 0:
            action = 'BUY'
            reason = f"Bullish reversal in SIDEWAYS market + Positive sentiment"
            confidence = (reversal['confidence'] + abs(sentiment['score'])) / 2
        
        # SELL signal: Bearish reversal or negative sentiment
        elif reversal['is_bearish_reversal'] or sentiment['score'] < -0.2:
            action = 'SELL'
            reason = f"Bearish reversal or negative sentiment detected"
            confidence = (reversal['confidence'] + abs(sentiment['score'])) / 2
        
        # HOLD: No clear signal
        else:
            action = 'HOLD'
            reason = "No clear reversal pattern detected"
            confidence = 0.5
        
        # Compile full result
        result = {
            'action': action,
            'reason': reason,
            'confidence': confidence,
            'current_price': current_price,
            'stop_loss': risk_levels['stop_loss_price'],
            'take_profit': risk_levels['take_profit_price'],
            'risk_reward_ratio': risk_levels['risk_reward_ratio'],
            'modules': {
                'regime': regime,
                'sentiment': sentiment,
                'risk_levels': risk_levels,
                'reversal': reversal
            }
        }
        
        logger.info(f"✅ Advanced AI Decision: {action} (Confidence: {confidence:.2%})")
        logger.info(f"   Reason: {reason}")
        
        return result