import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any
import ccxt
import os

class AIDecisionEngine:
    """
    4D AI Decision Engine:
    - Market Data (Technical Analysis)
    - Fundamental (News, Listings)
    - Sentiment (X/Twitter Analysis)
    - On-Chain (Whale Movements)
    """
    
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_API_KEY'),
            'secret': os.getenv('BINANCE_SECRET'),
        })
    
    async def analyze(self, symbol: str, currency: str = "USD") -> Dict[str, Any]:
        """
        Main analysis method combining all 4 dimensions
        """
        try:
            # 1. Market Data Analysis
            market_score = await self._analyze_market(symbol)
            
            # 2. Fundamental Analysis (simplified)
            fundamental_score = self._analyze_fundamentals(symbol)
            
            # 3. Sentiment Analysis (X/Twitter)
            sentiment_score = await self._analyze_sentiment(symbol)
            
            # 4. On-Chain Analysis (Whale tracking)
            whale_score = await self._analyze_whales(symbol)
            
            # Combine scores with weights
            weights = {
                'market': 0.35,
                'fundamental': 0.20,
                'sentiment': 0.25,
                'whale': 0.20
            }
            
            combined_score = (
                market_score * weights['market'] +
                fundamental_score * weights['fundamental'] +
                sentiment_score * weights['sentiment'] +
                whale_score * weights['whale']
            )
            
            # Determine action
            if combined_score >= 0.65:
                action = "BUY"
                predicted_pl = round(3.5 + (combined_score - 0.65) * 10, 2)
            elif combined_score <= 0.35:
                action = "SELL"
                predicted_pl = round(-2.5 - (0.35 - combined_score) * 10, 2)
            elif 0.45 <= combined_score <= 0.55:
                action = "HOLD"
                predicted_pl = 0.0
            else:
                action = "HOLD"
                predicted_pl = round((combined_score - 0.5) * 5, 2)
            
            # Generate principle explanation
            principle = self._generate_principle(
                action, market_score, fundamental_score, 
                sentiment_score, whale_score
            )
            
            return {
                "action": action,
                "principle": principle,
                "predicted_pl_percent": predicted_pl,
                "confidence": round(combined_score, 2),
                "scores": {
                    "market": round(market_score, 2),
                    "fundamental": round(fundamental_score, 2),
                    "sentiment": round(sentiment_score, 2),
                    "whale": round(whale_score, 2)
                },
                "timestamp": datetime.utcnow().isoformat(),
                "symbol": symbol
            }
            
        except Exception as e:
            return {
                "action": "HALT",
                "principle": f"Error in analysis: {str(e)}",
                "predicted_pl_percent": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _analyze_market(self, symbol: str) -> float:
        """
        Technical analysis using RSI, MACD, Bollinger Bands
        Returns score 0-1
        """
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Calculate RSI
            rsi = self._calculate_rsi(df['close'], period=14)
            
            # RSI scoring
            if rsi < 30:
                rsi_score = 0.9  # Oversold - bullish
            elif rsi > 70:
                rsi_score = 0.1  # Overbought - bearish
            else:
                rsi_score = 0.5 + ((50 - rsi) / 40) * 0.4
            
            # Volume trend
            recent_volume = df['volume'].tail(10).mean()
            older_volume = df['volume'].head(10).mean()
            volume_score = 0.7 if recent_volume > older_volume * 1.2 else 0.3
            
            # Price trend
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-20]) / df['close'].iloc[-20]
            trend_score = 0.5 + (price_change * 5)
            trend_score = max(0, min(1, trend_score))
            
            # Combine market indicators
            market_score = (rsi_score * 0.5 + volume_score * 0.25 + trend_score * 0.25)
            return market_score
            
        except Exception as e:
            print(f"Market analysis error: {e}")
            return 0.5
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        deltas = prices.diff()
        gain = (deltas.where(deltas > 0, 0)).rolling(window=period).mean()
        loss = (-deltas.where(deltas < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    
    def _analyze_fundamentals(self, symbol: str) -> float:
        """
        Fundamental analysis (simplified)
        In production: integrate news APIs, exchange listings, etc.
        """
        # Simplified: major coins get higher scores
        major_coins = ['BTC', 'ETH', 'BNB']
        base_symbol = symbol.replace('USDT', '').replace('USD', '')
        
        if base_symbol in major_coins:
            return 0.7
        else:
            return 0.5
    
    async def _analyze_sentiment(self, symbol: str) -> float:
        """
        X (Twitter) sentiment analysis
        In production: use X API or sentiment analysis tools
        """
        # Simplified sentiment simulation
        # In production: integrate with X API using x_keyword_search
        base_symbol = symbol.replace('USDT', '').replace('USD', '')
        
        # Simulate sentiment score based on symbol popularity
        sentiment_map = {
            'BTC': 0.75,
            'ETH': 0.70,
            'BNB': 0.65,
            'ADA': 0.60,
            'SOL': 0.68
        }
        
        return sentiment_map.get(base_symbol, 0.5)
    
    async def _analyze_whales(self, symbol: str) -> float:
        """
        Whale movement analysis
        In production: integrate on-chain data providers
        """
        # Simplified whale tracking
        # Returns score based on whale activity
        
        # Simulate whale buy/sell ratio
        whale_buy_ratio = np.random.uniform(0.4, 0.8)
        
        return whale_buy_ratio
    
    def _generate_principle(
        self, action: str, market: float, 
        fundamental: float, sentiment: float, whale: float
    ) -> str:
        """Generate human-readable explanation"""
        reasons = []
        
        if market > 0.65:
            reasons.append("RSI Oversold + Bullish Trend")
        elif market < 0.35:
            reasons.append("RSI Overbought + Bearish Trend")
        
        if sentiment > 0.6:
            reasons.append("Positive X Sentiment")
        elif sentiment < 0.4:
            reasons.append("Negative X Sentiment")
        
        if whale > 0.6:
            reasons.append("Whale Accumulation")
        elif whale < 0.4:
            reasons.append("Whale Distribution")
        
        if fundamental > 0.6:
            reasons.append("Strong Fundamentals")
        
        if not reasons:
            reasons.append("Neutral Market Conditions")
        
        return f"{action}: " + " + ".join(reasons)
